import json
from typing import Dict, List, Optional, Tuple
from django.contrib.auth.models import User
from django.db.models import Avg, Q
from django.utils import timezone
from thefuzz import fuzz
import statistics
import re

def normalize_competency_name(name: str) -> str:
    """Normaliza el nombre de una competencia para comparación"""
    # Eliminar espacios extras y convertir a minúsculas
    normalized = name.lower().strip()
    # Remover palabras comunes que no afectan el significado
    common_words = ['y', 'en', 'de', 'los', 'las', 'sistemas']
    for word in common_words:
        normalized = normalized.replace(f' {word} ', ' ')
    # Normalizar caracteres especiales
    normalized = re.sub(r'[áàäâ]', 'a', normalized)
    normalized = re.sub(r'[éèëê]', 'e', normalized)
    normalized = re.sub(r'[íìïî]', 'i', normalized)
    normalized = re.sub(r'[óòöô]', 'o', normalized)
    normalized = re.sub(r'[úùüû]', 'u', normalized)
    normalized = re.sub(r'[ñ]', 'n', normalized)
    # Eliminar caracteres especiales y múltiples espacios
    normalized = re.sub(r'[^a-z0-9\s]', '', normalized)
    normalized = ' '.join(normalized.split())
    return normalized

def find_matching_competency(competency_name: str) -> Tuple[Optional['Competency'], str, float]:
    """
    Encuentra la competencia más cercana usando matching exacto, fuzzy o comodín
    Retorna: (competencia, tipo_de_match, score_de_similitud)
    """
    from .models import Competency, CompetencyMismatchLog
    
    normalized_name = normalize_competency_name(competency_name)
    
    # Nivel 1: Match exacto
    try:
        comp = Competency.objects.get(name__iexact=normalized_name)
        return comp, 'exact', 100.0
    except Competency.DoesNotExist:
        pass
    
    # Nivel 2: Fuzzy matching
    all_comps = Competency.objects.all()
    matches = []
    
    for comp in all_comps:
        # Ratio de similitud general
        ratio = fuzz.ratio(normalized_name, normalize_competency_name(comp.name))
        # Token sort ratio (ignora orden de palabras)
        token_ratio = fuzz.token_sort_ratio(competency_name, comp.name)
        # Partial ratio (para subcadenas)
        partial_ratio = fuzz.partial_ratio(competency_name, comp.name)
        
        # Promedio ponderado de los ratios
        avg_ratio = (ratio * 0.4 + token_ratio * 0.4 + partial_ratio * 0.2)
        
        if avg_ratio > 80:  # Umbral de similitud
            matches.append((comp, avg_ratio))
    
    if matches:
        # Retornar la competencia con mayor similitud
        best_match = max(matches, key=lambda x: x[1])
        return best_match[0], 'fuzzy', best_match[1]
    
    # Nivel 3: Comodín basado en términos clave
    try:
        if any(term in normalized_name for term in ['matematica', 'numero', 'algebra', 'geometria']):
            comp = Competency.objects.get(name="Otras Competencias Matemáticas")
            return comp, 'wildcard', 0.0
        elif any(term in normalized_name for term in ['fisica', 'mecanica', 'energia']):
            comp = Competency.objects.get(name="Otras Competencias en Física")
            return comp, 'wildcard', 0.0
    except Competency.DoesNotExist:
        pass
    
    return None, 'none', 0.0

def update_competency_match_log(original_name: str, matched_competency: 'Competency', 
                              match_type: str, similarity_score: float):
    """Actualiza el registro de coincidencias de competencias"""
    from .models import CompetencyMismatchLog
    
    log, created = CompetencyMismatchLog.objects.get_or_create(
        original_name=original_name,
        matched_competency=matched_competency,
        defaults={
            'match_type': match_type,
            'similarity_score': similarity_score,
            'frequency': 1
        }
    )
    
    if not created:
        log.frequency += 1
        log.last_seen = timezone.now()
        if match_type == 'fuzzy':
            log.similarity_score = similarity_score
        log.save()

def analyze_feedback_for_competencies(feedback: str, student: User) -> Dict:
    """Analiza el feedback estructurado del LLM para extraer análisis por competencia"""
    try:        
        feedback_data = json.loads(feedback)
    except json.JSONDecodeError:
        return {'success': False, 'error': 'El feedback no está en formato JSON válido'}

    from .models import Competency, CompetencyAssessment, StudentCompetency

    results = {
        'success': True,
        'competency_updates': [],
        'error': None
    }

    for comp_analysis in feedback_data.get('competency_analysis', []):
        competency_name = comp_analysis['competency_name']
        
        # Buscar competencia usando el sistema de matching
        competency, match_type, similarity_score = find_matching_competency(competency_name)
        
        if competency:
            try:
                # Registrar el match en el log
                update_competency_match_log(
                    competency_name, competency, match_type, similarity_score
                )
                
                # Crear o actualizar CompetencyAssessment
                assessment = CompetencyAssessment.objects.create(
                    student=student,
                    competency=competency,
                    score=comp_analysis['demonstrated_level'],
                    llm_feedback=json.dumps(comp_analysis, ensure_ascii=False),
                    recommendations={
                        'strengths': comp_analysis['strengths'],
                        'areas_for_improvement': comp_analysis['areas_for_improvement'],
                        'recommendations': comp_analysis['recommendations'],
                        'match_type': match_type,
                        'similarity_score': similarity_score
                    }
                )

                # Actualizar StudentCompetency
                student_comp, _ = StudentCompetency.objects.get_or_create(
                    student=student,
                    competency=competency,
                    defaults={'level': 0}
                )
                
                # Actualizar nivel basado en el promedio histórico
                avg_level = CompetencyAssessment.objects.filter(
                    student=student,
                    competency=competency
                ).aggregate(Avg('score'))['score__avg']
                
                if avg_level:
                    student_comp.level = int(avg_level)
                    student_comp.last_assessed = timezone.now()
                    student_comp.save()

                results['competency_updates'].append({
                    'competency': competency_name,
                    'matched_to': competency.name,
                    'match_type': match_type,
                    'similarity': similarity_score,
                    'level': student_comp.level,
                    'assessment_id': assessment.id
                })

            except Exception as e:
                results['error'] = f"Error procesando competencia {competency_name}: {str(e)}"
                continue
        else:
            results['competency_updates'].append({
                'competency': competency_name,
                'matched_to': None,
                'match_type': 'none',
                'error': 'No se encontró competencia coincidente'
            })

    return results

def analyze_evaluation_results(student: User, evaluation_data: Dict) -> Dict:
    """Analyze evaluation results to identify strengths and weaknesses"""
    competency_scores = {}
    for question in evaluation_data.get('questions', []):
        competency = question.get('competency')
        if competency:
            if competency not in competency_scores:
                competency_scores[competency] = []
            competency_scores[competency].append(question.get('score', 0))
    
    analysis = {
        'competency_averages': {},
        'weak_areas': [],
        'strong_areas': []
    }
    
    for competency, scores in competency_scores.items():
        avg = statistics.mean(scores)
        analysis['competency_averages'][competency] = avg
        if avg < 60:
            analysis['weak_areas'].append(competency)
        elif avg > 80:
            analysis['strong_areas'].append(competency)
    
    return analysis

def generate_adaptive_recommendations(student: User) -> Dict:
    """Generate personalized learning recommendations based on student performance"""
    from .models import CompetencyAssessment, StudentCompetency, LearningResource
    
    # Get student's recent assessments
    recent_assessments = CompetencyAssessment.objects.filter(
        student=student
    ).order_by('-completed_at')[:5]
    
    # Get current competency levels
    competency_levels = StudentCompetency.objects.filter(
        student=student
    ).select_related('competency')
    
    recommendations = {
        'priority_competencies': [],
        'suggested_resources': [],
        'learning_path_adjustments': []
    }
    
    # Identify areas needing improvement
    weak_competencies = competency_levels.filter(level__lt=60)
    for comp in weak_competencies:
        # Find appropriate resources
        resources = LearningResource.objects.filter(
            competency=comp.competency,
            difficulty_level__lte=3  # Start with easier resources
        )[:3]
        
        recommendations['priority_competencies'].append({
            'competency': comp.competency.name,
            'current_level': comp.level,
            'resources': list(resources.values('id', 'title', 'content_type', 'estimated_duration'))
        })
    
    return recommendations

def update_learning_path(student: User, competency_id: int) -> Dict:
    """Update learning path based on student progress"""
    from .models import LearningPath, LearningActivity, StudentCompetency
    
    try:
        path = LearningPath.objects.get(
            student=student,
            competency_id=competency_id,
            is_active=True
        )
        
        # Calculate progress from activities
        completed_activities = LearningActivity.objects.filter(
            learning_path=path,
            completed_at__isnull=False
        ).count()
        
        total_activities = LearningActivity.objects.filter(
            learning_path=path
        ).count()
        
        if total_activities > 0:
            progress = (completed_activities / total_activities) * 100
            path.current_level = int(progress)
            path.save()
            
        # Update student competency
        student_comp, _ = StudentCompetency.objects.get_or_create(
            student=student,
            competency_id=competency_id
        )
        student_comp.level = path.current_level
        student_comp.save()
        
        return {
            'success': True,
            'progress': path.current_level,
            'completed_activities': completed_activities,
            'total_activities': total_activities
        }
        
    except LearningPath.DoesNotExist:
        return {
            'success': False,
            'error': 'Learning path not found'
        }

def process_markdown_content(content: str, metadata: Optional[Dict] = None) -> Dict:
    """Process markdown content and extract metadata"""
    from markdown import markdown
    import re
    
    # Extract metadata if present
    meta = metadata or {}
    if content.startswith('---'):
        meta_match = re.match(r'---\n(.*?)\n---\n(.*)', content, re.DOTALL)
        if meta_match:
            try:
                meta.update(json.loads(meta_match.group(1)))
                content = meta_match.group(2)
            except json.JSONDecodeError:
                pass
    
    # Convert markdown to HTML
    html_content = markdown(content)
    
    # Extract images
    image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    images = re.findall(image_pattern, content)
    
    return {
        'html': html_content,
        'metadata': meta,
        'images': images
    }

def integrate_llm_feedback(assessment) -> str:
    """Generate personalized feedback using LLM"""
    try:
        from evaluations.llm_utils import get_llm_response
        
        # Prepare context for LLM
        context = {
            'competency': assessment.competency.name,
            'score': assessment.score,
            'student_level': assessment.student.competencies.get(
                competency=assessment.competency
            ).level
        }
        
        # Generate feedback prompt
        prompt = f"""
        As an educational AI assistant, provide personalized feedback for a student's assessment:
        
        Competency: {context['competency']}
        Score: {context['score']}
        Current Level: {context['student_level']}
        
        Please provide:
        1. A brief analysis of the performance
        2. Specific areas for improvement
        3. Actionable recommendations for learning
        4. Encouragement and motivation
        
        Format the response in a clear, constructive manner.
        """
        
        feedback = get_llm_response(prompt)
        return feedback
        
    except Exception as e:
        return f"Unable to generate feedback at this time. Error: {str(e)}"

def get_learning_recommendations(student: User, competency_id: int) -> List[Dict]:
    """Get personalized learning resource recommendations"""
    from .models import LearningResource, StudentCompetency
    
    try:
        student_comp = StudentCompetency.objects.get(
            student=student,
            competency_id=competency_id
        )
        
        # Adjust difficulty based on current level
        if student_comp.level < 30:
            max_difficulty = 2
        elif student_comp.level < 60:
            max_difficulty = 3
        elif student_comp.level < 80:
            max_difficulty = 4
        else:
            max_difficulty = 5
            
        # Get appropriate resources
        resources = LearningResource.objects.filter(
            competency_id=competency_id,
            difficulty_level__lte=max_difficulty
        ).order_by('difficulty_level')[:5]
        
        return [{
            'id': r.id,
            'title': r.title,
            'type': r.get_content_type_display(),
            'difficulty': r.difficulty_level,
            'duration': r.estimated_duration,
            'description': r.description
        } for r in resources]
        
    except StudentCompetency.DoesNotExist:
        return []

#!/bin/bash

# Ruta del directorio actual
current_directory=$(pwd)

# Nombre del directorio a crear
base_directory="QTI_Bank"

# Lista de nombres de subdirectorios a crear dentro de QTI_Bank
subdirectorios=(
    'Math_Algebra'
    'Math_Statistics'
    'Math_Geometry'
    'Math_Calculus'
    'Math_Trigonometry'
    'Math_Probability'
    'Math_Number Theory'
    'Math_Logic'
    'Math_Graphics'
    'Math_Tables'
    'Physics_Kinematics'
    'Physics_Waves'
    'Physics_Thermodynamics'
    'Physics_Electromagnetism'
    'Physics_Optics'
    'Physics_Mechanics'
    'Physics_Acoustics'
    'Physics_Astronomy'
    'Physics_Nuclear Physics'
    'Physics_Relativity'
    'Physics_Particle Physics'
    'Physics_Dynamics'
    'Physics_Energy'
)

# Crear el directorio base
mkdir -p "$current_directory/$base_directory"

# Iterar sobre la lista y crear los subdirectorios dentro de QTI_Bank
for sub_dir_name in "${subdirectorios[@]}"
do
    mkdir -p "$current_directory/$base_directory/$sub_dir_name"
    echo "Directorio '$sub_dir_name' creado en $current_directory/$base_directory"
done

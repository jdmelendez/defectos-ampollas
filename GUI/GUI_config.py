# =============================================== PATHS =============================================================

PATH_IMGS = "./GUI/Archivos/dataset/Imagenes"
PATH_ANNS = "./GUI/Archivos/dataset/Anotaciones"
PATH_IMGS_PINTADAS = "./GUI/Archivos/dataset/Imagenes_pintadas"
PATH_IMGS_TEMPORAL = "./GUI/Archivos/temp"

# Pyinstaller
# PATH_IMGS = "./Archivos/dataset/Imagenes"
# PATH_ANNS = "./Archivos/dataset/Anotaciones"
# PATH_IMGS_PINTADAS = "./Archivos/dataset/Imagenes_pintadas"
# PATH_IMGS_TEMPORAL = "./Archivos/temp"


# ========================================= COLORES SEGUN DEFECTO ===================================================
COLORES_DEFECTOS = {"MORF. CABEZA AMPOLLA": "green",
                    "IMP. AMPOLLA": "blue",
                    "MORF. CUELLO AMPOLLA": "red",
                    "IMP. BLISTER": "purple",
                    "AMPOLLA ERROR": 'black'
                    }
# COLORES_DEFECTOS = {"AMPOLLA COLOCACION": "orange",
#                     "AMPOLLA SOLIDOS": "green",
#                     "AMPOLLA SELLADO": "blue",
#                     "AMPOLLA SERIGRAFIA": "red",
#                     "AMPOLLA ROTURA": "yellow",
#                     "BLISTER SOLIDOS": "black",
#                     "AMPOLLA VAHO": "purple",
#                     "AMPOLLA SUCIA": "white"
#                     }

# ========================================= RESOLUCION DE IMAGEN ===================================================
ALTO_IMAGEN, ANCHO_IMAGEN = 544, 728


# ========================================= CLASES DEFECTOS ANOTACIONES ===============================================

# Los nombres han de ser igual que los nombres de los botones de la interfaz

DICCIONARIO_COORDENADAS_DEFECTOS = {"SIN DEFECTO": ["sin_defecto", '-', '0'],
                                    'MORF. CABEZA AMPOLLA': ['amp_morf_cabeza', '-', '1'],
                                    "MORF. CUELLO AMPOLLA": ["amp_morf_cuello", '-', '2'],
                                    "IMP. AMPOLLA": ["amp_imp", '-', '3'],
                                    "IMP. BLISTER": ["blis_imp", '-', '4']}

# "AMPOLLA VAHO": ["amp_vaho", '-', 5],
# "AMPOLLA SERIGRAFIA": ["amp_serif", '-', 6],
# "AMPOLLA COLOCACIÓN": ["amp_coloc", '-', 7],
# "BLISTER SOLIDOS": ["blis_solidos", '-', 8]}

# ========================================= CLASES TIPO AMPOLLA ==================================================

# Los nombres han de coincidir con la lista exitente en el ComBox

DICCIONARIO_COORDENADAS_PRODUCTO = {"BABE VITAMIN C+": ["babe_vitaminC", '-', 11],
                                    "BABE BICALM+": ["babe_bicalm", '-', 12],
                                    "BABE PROTEOS 2F*": ["babe_proteos2f", '-', 13]}

# Ampollas - Control de calidad

En este proyecto se persigue identificar diversas características de los blisters de ampollas generados en la linea.
Concretamente, el objetivo se ubica en diferenciar el tipo de blister con el que se está trabajando, es decir,
a que cliente pertenece, el tamaño de las ampollas, etc... y por otra parte, detectar los defectos que puedan haber
en el producto.

![Alt text](/BLISTER.jpg?raw=true "Blister de ampollas")

## Creación del dataset de imagenes y anotaciones

### Interfaz etiquetadora

Para ello, se ha elaborado una interfaz que permite etiquetar cada imagen obtenida en la linea. La etiqueta se consigue
a través de la interacción con la inferfaz, seleccionando tanto el **tipo de blister** como el **defecto** en cuestión,
y dibujando sobre la imagen este segundo.

![Alt text](/Interfaz.png?raw=true "Interfaz etiquetadora")

La cámara industrial captura imágenes y las almacena en una carpeta temporal, de la cual la interfaz las va cogiendo y situando en el visor. Una vez etiquetada la imagen, se crean 3 archivos. La imagen original, la imagen pintada, y un fichero .xml con las coordenadas de los defectos dibujados.

Como peculiaridad, la imagen del blister completo se encuentra formada por dos imágenes capturadas por dos cámaras contiguas, para obtener así una mayor resolución de estas. Por ello, en la interfaz se han de etiquetar las imagenes de 2 en 2.

### Nombre de los ficheros del dataset

El nombre de estos archivos sigue un patrón establecido, de manera que se verá tal que así:
- **Fecha_Hora_IdDefectos_IdCliente_I (para la camara Izquierda)**
- **Fecha_Hora_IdDefectos_IdCliente_D (para la camara Derecha)**

La etiqueta del tipo de defecto, sigue la siguiente leyenda:

-  0 --> Sin defecto 
-  1 --> Blister Defectuoso
-  2 --> Blister Incompleto
-  3 --> Sellado Ampolla
-  4 --> Solidos Ampolla
-  5 --> Serigrafía Ampolla
-  6 --> Dimension Ampollas

Por su parte, la etiqueta identificativa del cliente viene dada por la siguiente leyenda:

- 1 --> Cliente X
- 2 --> Cliente Y

## Deep Learning


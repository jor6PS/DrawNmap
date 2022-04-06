# DrawNmap

## Usage

```console
# python3 DrawNmap.py <nmap xml format>

~EJEMPLOS~

Archivo único
# python3 DrawNmap.py /examples/nmap1.xml

Múltiples archivos
# python3 DrawNmap.py /examples/*.xml

```

## Descripción

Herramienta desarrollada en Python para mostrar en un diagrama de red el contenido extraído de un escaneo nmap. En el diagrama se muestran los activos en cada uno de los nodos y es posible visualizar e interactuar a partir del resto de información obtenida, como los puertos abiertos.

## Desarrollo

- Mostrar los nodos en el diagrama de red a partir de un escaneo Nmap en formato XML
- Mostrar información útil en cada uno de los nodos al poner el puntero en el nodo
- Aplicar filtros para alterar el diagrama
  - Filtrar por puerto, mostrando únicamente los nodos que tengan el puerto seleccionado habilitado
  - Filtrar por etiquetas, que muestren por ejemplo solo los puertos relacionados con un entorno corporativo
- Mostrar los nodos de distinto color en base a la cantidad de puertos abiertos detectados

## Rquisitos

```console
# pip3 install plotly
# pip3 install dash
# pip3 install networkx
# pip3 install pandas
# pip3 install subprocess
```

## Apariencia

![Alt text](https://github.com/jorperse/DrawNmap/blob/main/Screenshots/drawnmap_vid.gif?raw=true "Estado actual")

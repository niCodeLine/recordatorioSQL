# recordatorioSQL

This package is to get my reminders in my virtual assistant. Most of them being birthdays.  
  
I use to do this by **JSON**, but converted it to **SQL** to make it more reliable.


## Usage

Since the package is called _pornos_ (my keyboard is half working and I misspelled *pronos*), I call the
function _tico_, forming then the word _pronos.tico_ (or _pornos.tico_ in this case), meaning forecast in spanish.  
  

It checks if the input _lugar_ (place) is a name or the coordinates of some place and continues with:

```python
jsonData = obtener_pronostico(location = 'mackay')
```

or

```python
float: lat = -21.1408
float: lon = 149.1851

jsonData = obtener_pronostico(coodinates = (lat, lon))
```

we proceed by calling the class **Owo** to clean the data getting the forcast of today and the next 5 days:

```python
owo = Owo(jsonData)

datosDia = owo.arreglo_del_dia()
datos5Dias = owo.arreglo_5_dias()
```

from here we create the HTML script, and take the screenshot of the card:

```python
html = generar_html(dataDia=datosDia, data5dias=datos5Dias)

sacar_screenshot(html=html)
```


## Features

- **SQL**: Very fast.


## Contributions

Contributions are welcome! If you have improvements or fixes, please send a pull request or open an issue in the GitHub repository.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contact

Nico Spok - nicospok@proton.me
GitHub: niCodeLine

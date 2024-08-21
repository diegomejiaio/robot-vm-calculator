import requests
import pandas as pd

# URL inicial del JSON
url = "https://prices.azure.com/api/retail/prices?$filter=armRegionName eq 'eastus' and (priceType eq 'Consumption' or (priceType eq 'Reservation' and reservationTerm eq '1 Year')) and serviceFamily eq 'Compute' and serviceName eq 'Virtual Machines'"

# Lista para acumular todos los items
all_items = []

while url:
    # Realizar la solicitud GET
    response = requests.get(url)

    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        # Convertir la respuesta JSON a un diccionario de Python
        data = response.json()
        
        # Agregar los items a la lista acumulada
        all_items.extend(data['Items'])
        
        # Obtener el enlace a la siguiente página
        url = data.get('NextPageLink')
        print(f"Obteniendo 1000 datos de {url}")
    else:
        print(f"Error al obtener los datos: {response.status_code}")
        url = None  # Detener el bucle si hay un error

# Convertir la lista completa a un DataFrame
df = pd.DataFrame(all_items)

# Guardar el DataFrame como un archivo CSV en el directorio actual
df.to_csv("azure_virtual_machines_prices.csv", index=False)

print("Archivo CSV guardado exitosamente en el directorio del proyecto.")

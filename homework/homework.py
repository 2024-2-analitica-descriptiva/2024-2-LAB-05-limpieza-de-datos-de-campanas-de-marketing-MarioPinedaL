"""
Escriba el codigo que ejecute la accion solicitada.
"""

# pylint: disable=import-outside-toplevel


def clean_campaign_data(input_dir="files/input/", output_dir="files/output/"):
    """
    En esta tarea se le pide que limpie los datos de una campaña de
    marketing realizada por un banco, la cual tiene como fin la
    recolección de datos de clientes para ofrecerls un préstamo.

    La información recolectada se encuentra en la carpeta
    files/input/ en varios archivos csv.zip comprimidos para ahorrar
    espacio en disco.

    Usted debe procesar directamente los archivos comprimidos (sin
    descomprimirlos). Se desea partir la data en tres archivos csv
    (sin comprimir): client.csv, campaign.csv y economics.csv.
    Cada archivo debe tener las columnas indicadas.

    Los tres archivos generados se almacenarán en la carpeta files/output/.

    client.csv:
    - client_id
    - age
    - job: se debe cambiar el "." por "" y el "-" por "_"
    - marital
    - education: se debe cambiar "." por "_" y "unknown" por pd.NA
    - credit_default: convertir a "yes" a 1 y cualquier otro valor a 0
    - mortage: convertir a "yes" a 1 y cualquier otro valor a 0

    campaign.csv:
    - client_id
    - number_contacts
    - contact_duration
    - previous_campaing_contacts
    - previous_outcome: cmabiar "success" por 1, y cualquier otro valor a 0
    - campaign_outcome: cambiar "yes" por 1 y cualquier otro valor a 0
    - last_contact_day: crear un valor con el formato "YYYY-MM-DD",
        combinando los campos "day" y "month" con el año 2022.

    economics.csv:
    - client_id
    - const_price_idx
    - eurobor_three_months



    """
    import os
    import pandas as pd
    import zipfile


    os.makedirs(output_dir, exist_ok=True)
    resultados = {
        "generated_files": [],
        "missing_columns": {}
    }

    # Inicializar los DataFrames donde se van a consolidar los datos
    client_all = pd.DataFrame()
    campaign_all = pd.DataFrame()
    economics_all = pd.DataFrame()

    # Procesar cada archivo ZIP en la carpeta de entrada
    for archivo in os.listdir(input_dir):
        if archivo.endswith('.zip'):
            zip_path = os.path.join(input_dir, archivo)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for csv_file in zip_ref.namelist():
                    # Leer el archivo CSV directamente desde el ZIP, usando la primera columna como índice
                    with zip_ref.open(csv_file) as file:
                        data = pd.read_csv(file, index_col=0)  # Usamos `index_col=0` para definir la primera columna como índice

                        # Verificar las columnas disponibles
                        print(f"Columnas disponibles en {csv_file}: {data.columns.tolist()}")

                        # ** Limpieza y procesamiento de datos **
                        # Generar client.csv
                        client_columns = ['age', 'job', 'marital', 'education', 'credit_default', 'mortgage']
                        missing_client_columns = [col for col in client_columns if col not in data.columns]
                        if not missing_client_columns:
                            client = data[client_columns].copy()
                            client.index.name = 'client_id'  # Renombrar el índice para que se mantenga como 'client_id'
                            client['job'] = client['job'].str.replace('.', '', regex=False).str.replace('-', '_', regex=False)
                            client['education'] = client['education'].str.replace('.', '_', regex=False).replace('unknown', pd.NA)
                            client['credit_default'] = client['credit_default'].apply(lambda x: 1 if x == 'yes' else 0)
                            client['mortgage'] = client['mortgage'].apply(lambda x: 1 if x == 'yes' else 0)
                            # Consolidar todos los clientes
                            client_all = pd.concat([client_all, client], axis=0)
                        else:
                            print(f"Advertencia: Las columnas necesarias para 'client.csv' no están en {csv_file}: {missing_client_columns}.")
                            resultados["missing_columns"]['client.csv'] = missing_client_columns

                        # Generar campaign.csv
                        campaign_columns = ['number_contacts', 'contact_duration', 'previous_campaign_contacts',
                                            'previous_outcome', 'campaign_outcome', 'day', 'month']
                        missing_campaign_columns = [col for col in campaign_columns if col not in data.columns]
                        if not missing_campaign_columns:
                            campaign = data[campaign_columns].copy()
                            campaign.index.name = 'client_id'  # Renombrar el índice
                            campaign['previous_outcome'] = campaign['previous_outcome'].apply(lambda x: 1 if x == 'success' else 0)
                            campaign['campaign_outcome'] = campaign['campaign_outcome'].apply(lambda x: 1 if x == 'yes' else 0)
                            # Corregir el procesamiento de la fecha para obtener un valor en formato 'YYYY-MM-DD'
                            campaign['last_contact_day'] = pd.to_datetime(
                                campaign['day'].astype(str) + '-' + campaign['month'] + '-2022',
                                format='%d-%b-%Y'
                            )
                            campaign = campaign.drop(columns=['day', 'month'])

                            # Cambiar el nombre de la columna 'last_contact_day' a 'last_contact_date'
                            campaign = campaign.rename(columns={'last_contact_day': 'last_contact_date'})

                            # Consolidar todos los campaigns
                            campaign_all = pd.concat([campaign_all, campaign], axis=0)
                        else:
                            print(f"Advertencia: Las columnas necesarias para 'campaign.csv' no están en {csv_file}: {missing_campaign_columns}.")
                            resultados["missing_columns"]['campaign.csv'] = missing_campaign_columns

                        # Generar economics.csv
                        economics_columns = ['cons_price_idx', 'euribor_three_months']
                        missing_economics_columns = [col for col in economics_columns if col not in data.columns]
                        if not missing_economics_columns:
                            economics = data[economics_columns].copy()
                            economics.index.name = 'client_id'  # Renombrar el índice
                            # Consolidar todos los economics
                            economics_all = pd.concat([economics_all, economics], axis=0)
                        else:
                            print(f"Advertencia: Las columnas necesarias para 'economics.csv' no están en {csv_file}: {missing_economics_columns}.")
                            resultados["missing_columns"]['economics.csv'] = missing_economics_columns

    # Guardar los DataFrames consolidados
    client_file = os.path.join(output_dir, 'client.csv')
    if not client_all.empty:
        client_all.to_csv(client_file)
        resultados["generated_files"].append(client_file)

    campaign_file = os.path.join(output_dir, 'campaign.csv')
    if not campaign_all.empty:
        campaign_all.to_csv(campaign_file)
        resultados["generated_files"].append(campaign_file)

    economics_file = os.path.join(output_dir, 'economics.csv')
    if not economics_all.empty:
        economics_all.to_csv(economics_file)
        resultados["generated_files"].append(economics_file)

    return resultados

if __name__ == "__main__":
    resultados = clean_campaign_data()
    print("Resumen del procesamiento:")
    print(resultados)

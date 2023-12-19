from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# MySQL connection settings
db_config = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "root",
    "database": "adc_strainlist",
}

with open('C:/Users/telka/PycharmProjects/pythonProject1/templates/load_gamma_table.html', 'r') as file:
    gamma_table_data = file.read()

def execute_query(query, params=None, fetch_all=True):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    if fetch_all:
        result = cursor.fetchall()
    else:
        result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/load_strains')
def load_strains():
    # Fetch all strain details from the database
    query = "SELECT * FROM strain_details"
    strains = execute_query(query)
    return render_template('load_strains.html', strains=strains)

@app.route('/search_strains', methods=['GET', 'POST'])
def search_strains():
    if request.method == 'POST':
        search_type = request.form.get('searchType')
        genus = request.form.get('genus', '').lower()
        species = request.form.get('species', '').lower()
        strain = request.form.get('strain', '').lower()

        # Create your SQL query based on the input values
        query = "SELECT * FROM strain_details WHERE 1"

        params = []  # Initialize an empty list for parameters

        if genus:
            query += " AND LOWER(Genus) = %s"
            params.append(genus)
        if species:
            query += " AND LOWER(Species) = %s"
            params.append(species)
        if strain:
            query += " AND LOWER(Strain) = %s"
            params.append(strain)

        # Execute the SQL query with the provided parameters
        strains = execute_query(query, params)

        # Fetch fermentation data based on search type
        fermentation_query = "SELECT * FROM fermentation_data_2ndjune WHERE "
        fermentation_params = []

        if genus:
            fermentation_query += "LOWER(Genus) = %s"
            fermentation_params.append(genus)
        elif species:
            fermentation_query += "LOWER(Species) = %s"
            fermentation_params.append(species)
        elif strain:
            fermentation_query += "LOWER(Strain) = %s"
            fermentation_params.append(strain)

        fermentation_data = execute_query(fermentation_query, fermentation_params)

        # Assign SigE_class based on Lib_Collection_ID
        for entry in fermentation_data:
            lib_collection_id = entry['Lib_Collection_ID']
            if lib_collection_id in [6, 12, 26, 33]:
                entry['SigE_class'] = 'SigE-lightgreen'
            elif lib_collection_id in [10, 17, 35, 38, 39]:
                entry['SigE_class'] = 'SigE-darkgreen'
            elif lib_collection_id == 37:
                entry['SigE_class'] = 'SigE-green'
            else:
                entry['SigE_class'] = ''  # Default class if not specified

        # Fetch data from the gamma table based on search criteria
        gamma_query = "SELECT * FROM gamma_table WHERE Genus = %s OR Species = %s OR Strain = %s"
        gamma_params = [genus, species, strain]
        gamma_data = execute_query(gamma_query, gamma_params)

        return render_template('search_strains.html', search_type=search_type, genus=genus, species=species, strains=strains, fermentation_data=fermentation_data, gamma_data=gamma_data, gamma_table_data=gamma_table_data)

    return render_template('search_strains.html')

@app.route('/parse_genome/<int:lib_collection_id>')
def parse_genome(lib_collection_id):
    query = "SELECT * FROM genome_data WHERE strain_details_Lib_Collection_ID = %s"
    params = (lib_collection_id,)
    genome_info = execute_query(query, params)
    return render_template('genome_information.html', genome_info=genome_info)

@app.route('/load_fermentation_data')
def load_fermentation_data():
    query = "SELECT * FROM fermentation_data_2ndjune"
    fermentation_data = execute_query(query)

    # Iterate through the fermentation_data and mark 'yes' in Pyoverdine with a flag
    for entry in fermentation_data:
        if entry['Pyoverdine'] == 'yes':
            entry['highlight'] = True  # Add a flag to highlight
        # Modify the class based on SigE values
        lib_collection_id = entry['Lib_Collection_ID']
        if lib_collection_id in [6, 12, 26, 33]:
            entry['SigE_class'] = 'SigE-lightgreen'
        elif lib_collection_id in [10, 17, 35, 38, 39]:
            entry['SigE_class'] = 'SigE-darkgreen'
        elif lib_collection_id == 37:
            entry['SigE_class'] = 'SigE-green'
        else:
            entry['SigE_class'] = ''  # Default class if not specified

    return render_template('load_fermentation_data.html', fermentation_data=fermentation_data)

@app.route('/load_gamma_table')
def load_gamma_table():
    # Retrieve data from your database for the gamma_table
    query = "SELECT * FROM gamma_table"  # Adjust this query accordingly
    gamma_data = execute_query(query)
    return render_template('load_gamma_table.html', gamma_data=gamma_data)

@app.route('/load_khani_gamma_table/<lib_collection_id>')
def load_khani_gamma_table(lib_collection_id=None):
    # If Lib_Collection_ID is '38', load the entire table of khani_gamma
    if lib_collection_id == '38':
        query = "SELECT * FROM khani_gamma"
        khani_gamma_data = execute_query(query)
        return render_template('load_khani_gamma_table.html', khani_gamma_data=khani_gamma_data)

    # If Lib_Collection_ID is not '38', redirect to load_gamma_table
    return redirect(url_for('load_gamma_table'))

if __name__ == '__main__':
    app.run(debug=True)

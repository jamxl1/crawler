import os
import pandas as pd
import requests

def process_csv_and_download_html(csv_path, output_csv_path, output_dir):
    # Stelle sicher, dass der Ausgabeordner existiert
    os.makedirs(output_dir, exist_ok=True)
    
    # Lese die CSV-Datei ein
    df = pd.read_csv(csv_path)
    
    # Stelle sicher, dass die CSV eine Spalte "Links" hat
    if "URL" not in df.columns:
        raise ValueError("Die CSV-Datei muss eine Spalte 'Links' enthalten.")
    
    # Füge eine neue Spalte für die Namen der gespeicherten HTML-Dateien hinzu
    df['HTML_Filename'] = None
    
    # Dictionary, um bereits heruntergeladene URLs zu verfolgen
    downloaded_urls = {}
    
    # Benutzerdefinierte Header für den Request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    
    for index, row in df.iterrows():
        url = row['URL']
        if url in downloaded_urls:
            # Verwende den bereits existierenden Dateinamen
            df.at[index, 'HTML_Filename'] = downloaded_urls[url]
        else:
            try:
                # Lade den HTML-Inhalt herunter mit Headern
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                # Erzeuge einen eindeutigen Dateinamen
                html_filename = f"{len(downloaded_urls) + 1}.html"
                html_path = os.path.join(output_dir, html_filename)
                
                # Speichere den HTML-Inhalt in einer Datei
                with open(html_path, 'w', encoding='utf-8') as file:
                    file.write(response.text)
                
                # Speichere die URL und den Dateinamen im Dictionary
                downloaded_urls[url] = html_filename
                df.at[index, 'HTML_Filename'] = html_filename
            except Exception as e:
                print(f"Fehler beim Verarbeiten von {url}: {e}")
                df.at[index, 'HTML_Filename'] = "Error"
    
    # Ordne die Spalten neu, um `HTML_Filename` an die erste Position zu setzen
    columns_order = ['HTML_Filename'] + [col for col in df.columns if col != 'HTML_Filename']
    df = df[columns_order]
    
    # Speichere die aktualisierte CSV-Datei
    df.to_csv(output_csv_path, index=False)
    print(f"Prozess abgeschlossen. Aktualisierte CSV gespeichert unter: {output_csv_path}")

# Beispielaufruf
csv_path = "input.csv"  # Pfad zur Eingabedatei
output_csv_path = "output.csv"  # Pfad zur aktualisierten Datei
output_dir = "downloaded_html"  # Ordner für gespeicherte HTML-Dateien

process_csv_and_download_html(csv_path, output_csv_path, output_dir)

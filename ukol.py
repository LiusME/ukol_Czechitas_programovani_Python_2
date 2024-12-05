import requests
import json


# Funkce pro vyhledání právní formy
def vyhledej_pravni_formu(kod, seznam):
    for polozka in seznam:
        if polozka["kod"] == kod:
            return polozka["nazev"]
    return "Neznámá právní forma"

def main():
    print("Vyberte možnost hledání subjektů: ")
    print("Vyhledání subjektu podle IČO - stiskněte 1.")
    print("Pro vyhledání subjektu podle názvu stiskněte 2.")
    vyber = input("Vaše volba: ")
    
    if vyber == "1":
        ico = input("hledané identifikační číslo osoby (IČO): ")
        url = f"https://ares.gov.cz/ekonomicke-subjekty-v-be/rest/ekonomicke-subjekty/{ico}"
        
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            obchodni_jmeno = data.get("obchodniJmeno", "Neznámé jméno")
            adresa = data.get("textovaAdresa", "Neznámá adresa")
            print(f"{obchodni_jmeno}\n{adresa}")
        else:
            print(f"Chyba při získávání dat: {response.status_code}")
    
    elif vyber == "2":
        nazev = input("Zadejte název subjektu: ")
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        data = json.dumps({"obchodniJmeno": nazev})
        response = requests.post(
            "https://ares.gov.cz/ekonomicke-subjekty-v-be/rest/ekonomicke-subjekty/vyhledat",
            headers=headers,
            data=data
        )
        
        if response.status_code == 200:
            vysledek = response.json()
            pocet_celkem = vysledek.get("pocetCelkem", 0)
            subjekty = vysledek.get("ekonomickeSubjekty", [])
            
            # Získání číselníku právních forem
            response_legal = requests.post(
                "https://ares.gov.cz/ekonomicke-subjekty-v-be/rest/ciselniky-nazevniky/vyhledat",
                headers=headers,
                data=json.dumps({"kodCiselniku": "PravniForma", "zdrojCiselniku": "res"})
            )
            legal_form_dict = {}
            if response_legal.status_code == 200:
                legal_data = response_legal.json()
                polozky_ciselniku = legal_data["ciselniky"][0]["polozkyCiselniku"]
                for polozka in polozky_ciselniku:
                    legal_form_dict[polozka["kod"]] = polozka["nazev"]
            
            print(f"Nalezeno subjektů: {pocet_celkem}")
            for subjekt in subjekty:
                obchodni_jmeno = subjekt.get("obchodniJmeno", "Neznámé jméno")
                ico = subjekt.get("ico", "Neznámé IČO")
                pravni_forma = vyhledej_pravni_formu(subjekt.get("pravniForma"), polozky_ciselniku)
                print(f"{obchodni_jmeno}, {ico}, {pravni_forma}")
        else:
            print(f"Chyba při získávání dat: {response.status_code}")


if __name__ == "__main__":
    main()
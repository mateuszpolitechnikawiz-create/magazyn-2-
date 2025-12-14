

📦 Poprawiony Kod Aplikacji Streamlit (app.py)
Ten kod jest gotowy do wdrożenia na Streamlit i używa st.session_state do zachowania stanu magazynu w trakcie interakcji.

Python

import streamlit as st
import pandas as pd

# --- Użycie st.session_state do przechowywania listy ---
# Sprawdza, czy lista 'magazyn' istnieje w stanie sesji.
# Jeśli nie, inicjuje ją domyślnymi danymi.
if 'magazyn' not in st.session_state:
    st.session_state.magazyn = [
        {"Towar": "Laptop Pro", "Ilość": 5, "Cena jednostkowa": 4500.00},
        {"Towar": "Monitor 27'", "Ilość": 12, "Cena jednostkowa": 1200.00},
        {"Towar": "Klawiatura Mechaniczna", "Ilość": 25, "Cena jednostkowa": 350.00}
    ]

# --- Funkcje Logiki Magazynu (CRUD na liście) ---

def dodaj_towar(towar, ilosc, cena):
    """Dodaje nowy towar do listy magazynu."""
    # Konwersja danych na odpowiednie typy przed dodaniem
    try:
        ilosc = int(ilosc)
        cena = float(cena)
    except ValueError:
        st.error("Ilość musi być liczbą całkowitą, a Cena musi być liczbą zmiennoprzecinkową (np. 1200.00).")
        return

    nowy_towar = {"Towar": towar, "Ilość": ilosc, "Cena jednostkowa": cena}
    st.session_state.magazyn.append(nowy_towar)
    st.success(f"Dodano: {towar} (Ilość: {ilosc})")

def usun_towar(indeks):
    """Usuwa towar z listy magazynu na podstawie indeksu."""
    if 0 <= indeks < len(st.session_state.magazyn):
        nazwa_usunieta = st.session_state.magazyn[indeks]['Towar']
        del st.session_state.magazyn[indeks]
        st.warning(f"Usunięto towar: {nazwa_usunieta}")
    else:
        st.error("Niepoprawny indeks towaru do usunięcia.")


# --- Interfejs Użytkownika Streamlit ---

st.title("📦 Prosty Magazyn (Demo Streamlit)")
st.caption("Dane są przechowywane w pamięci sesji i zostaną zresetowane po zamknięciu przeglądarki.")

# 1. WYŚWIETLANIE MAGAZYNU (READ)
st.header("Lista Aktualnych Towarów")

if st.session_state.magazyn:
    # Tworzenie DataFrame z listy słowników
    df_magazyn = pd.DataFrame(st.session_state.magazyn)
    # Dodanie kolumny z wartością całkowitą
    df_magazyn['Wartość'] = df_magazyn['Ilość'] * df_magazyn['Cena jednostkowa']
    
    # Wyświetlanie tabeli w Streamlit
    st.dataframe(df_magazyn, use_container_width=True, hide_index=True)
    
    # Podsumowanie
    st.markdown(f"**Łączna wartość magazynu:** **{df_magazyn['Wartość'].sum():,.2f}** PLN")
else:
    st.info("Magazyn jest obecnie pusty.")

# --- SEKCJA DODAWANIA TOWARU (CREATE) ---
st.header("➕ Dodaj Nowy Towar")

with st.form("form_dodaj_towar", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        nowy_towar = st.text_input("Nazwa Towaru", key="input_towar")
    with col2:
        nowa_ilosc = st.number_input("Ilość", min_value=1, value=1, step=1, key="input_ilosc")
    with col3:
        nowa_cena = st.number_input("Cena jednostkowa (PLN)", min_value=0.01, value=100.00, step=0.50, format="%.2f", key="input_cena")

    submitted = st.form_submit_button("Dodaj do Magazynu")
    if submitted and nowy_towar:
        dodaj_towar(nowy_towar, nowa_ilosc, nowa_cena)
        # POPRAWKA: Użycie st.rerun() zamiast st.experimental_rerun()
        st.rerun()
    elif submitted and not nowy_towar:
        st.error("Proszę podać nazwę towaru.")


# --- SEKCJA USUWANIA TOWARU (DELETE) ---
st.header("➖ Usuń Towar")

if st.session_state.magazyn:
    # Tworzymy listę opcji do wyboru w dropdownie
    opcje_usuwania = [f"{i}: {item['Towar']} (Ilość: {item['Ilość']})" 
                      for i, item in enumerate(st.session_state.magazyn)]
    
    wybrany_do_usuniecia = st.selectbox(
        "Wybierz towar do usunięcia (cała pozycja):",
        options=opcje_usuwania,
        index=0 # Domyślnie wybrany jest pierwszy element
    )
    
    # Wyciągamy indeks z wybranego stringa (jest on na początku)
    # Przykład: "0: Laptop Pro (Ilość: 5)" -> indeks to 0
    indeks_do_usuniecia = int(wybrany_do_usuniecia.split(":")[0])

    if st.button("Usuń wybrany Towar", help="Spowoduje trwałe usunięcie całej pozycji z magazynu"):
        usun_towar(indeks_do_usuniecia)
        # POPRAWKA: Użycie st.rerun() zamiast st.experimental_rerun()
        st.rerun()
else:
    st.info("Brak towarów do usunięcia.")

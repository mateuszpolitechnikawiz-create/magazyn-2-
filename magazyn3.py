import streamlit as st
import pandas as pd

# Ustawienie konfiguracji strony
st.set_page_config(
    page_title="Rozbudowany Magazyn",
    layout="wide"
)

# --- Użycie st.session_state do przechowywania listy ---
if 'magazyn' not in st.session_state:
    st.session_state.magazyn = [
        {"Towar": "Laptop Pro", "Ilość": 5, "Cena jednostkowa": 4500.00},
        {"Towar": "Monitor 27'", "Ilość": 12, "Cena jednostkowa": 1200.00},
        {"Towar": "Klawiatura Mechaniczna", "Ilość": 25, "Cena jednostkowa": 350.00},
        {"Towar": "Myszka bezprzewodowa", "Ilość": 50, "Cena jednostkowa": 120.00},
    ]

# --- Funkcje Logiki Magazynu ---

def dodaj_towar_handler(towar, ilosc, cena):
    """Obsługa dodawania nowego towaru."""
    if not towar:
        st.error("Proszę podać nazwę towaru.")
        return

    try:
        ilosc = int(ilosc)
        cena = float(cena)
    except ValueError:
        st.error("Błąd: Ilość musi być liczbą całkowitą, a Cena zmiennoprzecinkową.")
        return

    nowy_towar = {"Towar": towar, "Ilość": ilosc, "Cena jednostkowa": cena}
    st.session_state.magazyn.append(nowy_towar)
    st.success(f"Dodano: **{towar}** (Ilość: {ilosc})")
    st.rerun()

def usun_towar_handler(indeks):
    """Obsługa usuwania towaru na podstawie indeksu."""
    if 0 <= indeks < len(st.session_state.magazyn):
        nazwa_usunieta = st.session_state.magazyn[indeks]['Towar']
        del st.session_state.magazyn[indeks]
        st.warning(f"Usunięto towar: **{nazwa_usunieta}**")
        st.rerun()
    else:
        st.error("Wystąpił błąd podczas usuwania. Niepoprawny indeks.")

def zapisz_zmiany_handler(edited_df):
    """Obsługuje zapis zmian edytowanych bezpośrednio w st.data_editor."""
    # Tworzymy nową listę słowników ze zmienionego DataFrame
    nowa_lista = edited_df.to_dict('records')
    # Sprawdzamy, czy w liście nie ma błędnych wartości (np. Ilość ujemna)
    if any(item['Ilość'] < 0 for item in nowa_lista):
        st.error("Ilość towaru nie może być ujemna. Zmiany nie zostały zapisane.")
        return
        
    st.session_state.magazyn = nowa_lista
    st.success("Zapisano zmiany w magazynie!")
    st.rerun()

# --- Interfejs Użytkownika Streamlit ---

st.title("📦 Rozbudowany System Magazynowy")
st.caption("Aplikacja obsługuje dodawanie, usuwanie, edycję i filtrowanie towarów.")

# --- FILTRACJA (Sidebar) ---
st.sidebar.header("🔍 Opcje Filtrowania")
search_term = st.sidebar.text_input("Szukaj po nazwie towaru:")

# Konwersja listy do DataFrame dla łatwiejszej filtracji
df_magazyn = pd.DataFrame(st.session_state.magazyn)

if not df_magazyn.empty:
    # Zastosowanie filtra
    if search_term:
        df_filtered = df_magazyn[
            df_magazyn['Towar'].str.contains(search_term, case=False, na=False)
        ]
    else:
        df_filtered = df_magazyn.copy()

    # Dodanie kolumny Wartość
    df_filtered['Wartość'] = df_filtered['Ilość'] * df_filtered['Cena jednostkowa']
    df_filtered = df_filtered.round({'Wartość': 2}) # Zaokrąglenie wartości pieniężnych
    
    # Użycie st.data_editor dla interaktywnej edycji
    st.header("Lista Aktualnych Towarów (Edytowalna)")
    
    # Konfiguracja edycji kolumn
    edited_df = st.data_editor(
        df_filtered,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Ilość": st.column_config.NumberColumn(
                "Ilość",
                help="Edytuj stan magazynowy (liczba całkowita)",
                min_value=0,
                step=1,
                format="%d"
            ),
            "Cena jednostkowa": st.column_config.NumberColumn(
                "Cena jednostkowa",
                help="Edytuj cenę jednostkową (PLN)",
                format="%.2f PLN"
            ),
            "Wartość": st.column_config.NumberColumn(
                "Wartość",
                help="Wartość całkowita. Obliczana automatycznie.",
                disabled=True, # Nie można edytować
                format="%.2f PLN"
            ),
        }
    )

    # Przycisk ZAPISZ ZMIANY (Update)
    # Sprawdzamy, czy edytowany DataFrame różni się od oryginalnego
    if not edited_df.equals(df_filtered):
        if st.button("💾 Zapisz Zmiany Edytowane w Tabeli", key="save_edits"):
            # Ponieważ st.data_editor zwraca tylko to, co jest aktualnie filtrowane, 
            # musimy mieć osobną logikę zapisu w celu poprawnego scalenia z oryginalnym df_magazyn.
            # Z uwagi na prostotę, zapisujemy cały edytowany df_filtered jako nową listę magazynu.
            # (Uwaga: to działa tylko dlatego, że edytujemy i wyświetlamy 'df_filtered',
            # jeśli filtr jest aktywny, zapisujemy tylko przefiltrowaną część).
            
            # Najprostsze rozwiązanie dla tego demo: upewnij się, że użytkownik edytuje tylko
            # wtedy, gdy nie ma aktywnego filtru, lub zaimplementuj zaawansowane scalanie.
            # Dla celów tego zadania, przechowujemy tylko rekordy edytowane (df_filtered).
            
            if search_term:
                 st.error("Zmiany można zapisywać tylko, gdy nie jest aktywny filtr wyszukiwania.")
            else:
                 zapisz_zmiany_handler(edited_df)


    # Podsumowanie
    st.markdown(f"**Łączna wartość aktualnie wyświetlonego towaru:** **{df_filtered['Wartość'].sum():,.2f}** PLN")
else:
    st.info("Magazyn jest obecnie pusty lub nie znaleziono towarów pasujących do filtra.")

st.divider()

# --- SEKCJA DODAWANIA I USUWANIA ---
col_add, col_remove = st.columns(2)

with col_add:
    # --- DODAWANIE TOWARU (CREATE) ---
    st.header("➕ Dodaj Nowy Towar")

    nowy_towar = st.text_input("Nazwa Towaru", key="input_towar_add", value="")
    col_a, col_b = st.columns(2)
    with col_a:
        nowa_ilosc = st.number_input("Ilość", min_value=1, value=1, step=1, key="input_ilosc_add")
    with col_b:
        nowa_cena = st.number_input("Cena jednostkowa (PLN)", min_value=0.01, value=100.00, step=0.50, format="%.2f", key="input_cena_add")
    
    if st.button("Dodaj do Magazynu", key="submit_add"):
        dodaj_towar_handler(nowy_towar, nowa_ilosc, nowa_cena)


with col_remove:
    # --- USUWANIE TOWARU (DELETE) ---
    st.header("➖ Usuń Towar")

    if st.session_state.magazyn:
        # Tworzymy listę opcji do wyboru
        opcje_usuwania = [f"{i}: {item['Towar']} (Ilość: {item['Ilość']})" 
                          for i, item in enumerate(st.session_state.magazyn)]
        
        wybrany_do_usuniecia_str = st.selectbox(
            "Wybierz towar do usunięcia (cała pozycja):",
            options=opcje_usuwania,
            index=0,
            key="select_remove"
        )
        
        indeks_do_usuniecia = int(wybrany_do_usuniecia_str.split(":")[0])

        if st.button("Usuń wybrany Towar", key="submit_remove", help="Spowoduje trwałe usunięcie całej pozycji z magazynu"):
            usun_towar_handler(indeks_do_usuniecia)
    else:
        st.info("Brak towarów do usunięcia.")

import streamlit as st
import pandas as pd
from datetime import datetime

# Ustawienie konfiguracji strony
st.set_page_config(
    page_title="Rozbudowany Magazyn",
    layout="wide"
)

# --- Użycie st.session_state do przechowywania list ---
if 'magazyn' not in st.session_state:
    st.session_state.magazyn = [
        {"Towar": "Laptop Pro", "Ilość": 5, "Cena jednostkowa": 4500.00},
        {"Towar": "Monitor 27'", "Ilość": 12, "Cena jednostkowa": 1200.00},
        {"Towar": "Klawiatura Mechaniczna", "Ilość": 25, "Cena jednostkowa": 350.00},
        {"Towar": "Myszka bezprzewodowa", "Ilość": 50, "Cena jednostkowa": 120.00},
    ]

# Nowa lista do przechowywania zamówień
if 'zamowienia' not in st.session_state:
    st.session_state.zamowienia = []


# --- Funkcje Logiki Magazynu i Zamówień ---

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
    nowa_lista = edited_df.to_dict('records')
    if any(item['Ilość'] < 0 for item in nowa_lista):
        st.error("Ilość towaru nie może być ujemna. Zmiany nie zostały zapisane.")
        return
        
    st.session_state.magazyn = nowa_lista
    st.success("Zapisano zmiany w magazynie!")
    st.rerun()
    
def zloz_zamowienie_handler(nazwa_towaru, ilosc_zamawiana):
    """Obsługa składania zamówienia: aktualizuje magazyn i dodaje do historii."""
    try:
        ilosc_zamawiana = int(ilosc_zamawiana)
    except ValueError:
        st.error("Ilość zamawiana musi być liczbą całkowitą.")
        return

    if ilosc_zamawiana <= 0:
        st.error("Ilość zamawiana musi być większa niż zero.")
        return
        
    # Znajdź towar w magazynie
    znaleziono = False
    for item in st.session_state.magazyn:
        if item['Towar'] == nazwa_towaru:
            znaleziono = True
            
            if item['Ilość'] >= ilosc_zamawiana:
                # 1. Aktualizacja magazynu
                item['Ilość'] -= ilosc_zamawiana
                cena = item['Cena jednostkowa']
                wartosc_zamowienia = ilosc_zamawiana * cena
                
                # 2. Dodanie do listy zamówień
                nowe_zamowienie = {
                    "Data": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Towar": nazwa_towaru,
                    "Ilość": ilosc_zamawiana,
                    "Cena jednostkowa": cena,
                    "Wartość": wartosc_zamowienia
                }
                st.session_state.zamowienia.append(nowe_zamowienie)
                
                st.success(f"✅ Złożono zamówienie: {nazwa_towaru} x {ilosc_zamawiana}")
                st.rerun()
                return # Wyjdź po sukcesie

            else:
                st.error(f"❌ Brak wystarczającej ilości towaru. Dostępnych: {item['Ilość']}")
                return # Wyjdź po błędzie braku ilości

    if not znaleziono:
        st.error(f"Towar '{nazwa_towaru}' nie znajduje się w magazynie.")


# --- Interfejs Użytkownika Streamlit ---

st.title("📦 Rozbudowany System Magazynowy")

# --- FILTRACJA (Sidebar) ---
st.sidebar.header("🔍 Opcje Filtrowania")
search_term = st.sidebar.text_input("Szukaj po nazwie towaru:")
st.sidebar.divider()
st.sidebar.subheader("Historia Zamówień")

# Konwersja listy do DataFrame dla wyświetlenia (READ)
df_magazyn = pd.DataFrame(st.session_state.magazyn)

# --- WYŚWIETLANIE MAGAZYNU (Edytowalna Tabela) ---
st.header("Lista Aktualnych Towarów (Edytowalna)")

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
    df_filtered = df_filtered.round({'Wartość': 2})
    
    # Interaktywna edycja
    edited_df = st.data_editor(
        df_filtered,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Ilość": st.column_config.NumberColumn("Ilość", min_value=0, step=1, format="%d"),
            "Cena jednostkowa": st.column_config.NumberColumn("Cena jednostkowa", format="%.2f PLN"),
            "Wartość": st.column_config.NumberColumn("Wartość", disabled=True, format="%.2f PLN"),
        }
    )

    # Przycisk ZAPISZ ZMIANY (Update)
    if not edited_df.equals(df_filtered):
        if st.button("💾 Zapisz Zmiany Edytowane w Tabeli", key="save_edits"):
            if search_term:
                 st.warning("Aby zapisać zmiany, wyczyść filtr wyszukiwania.")
            else:
                 zapisz_zmiany_handler(edited_df)

    st.markdown(f"**Łączna wartość aktualnie wyświetlonego towaru:** **{df_filtered['Wartość'].sum():,.2f}** PLN")
else:
    st.info("Magazyn jest obecnie pusty lub nie znaleziono towarów pasujących do filtra.")

st.divider()

# --- SEKCJA ZAMÓWIEŃ, DODAWANIA I USUWANIA ---
col_order, col_manage = st.columns(2)

with col_order:
    # --- NOWA SEKCJA: SKŁADANIE ZAMÓWIENIA ---
    st.header("🛒 Złóż Zamówienie")
    
    # Lista dostępnych towarów do wyboru
    opcje_towarow = [item['Towar'] for item in st.session_state.magazyn]
    
    if opcje_towarow:
        towar_do_zamowienia = st.selectbox("Wybierz towar:", options=opcje_towarow, key="select_order_item")
        ilosc_zamawiana = st.number_input("Ilość do zamówienia", min_value=1, value=1, step=1, key="input_order_qty")
        
        if st.button("Złóż Zamówienie", key="submit_order"):
            zloz_zamowienie_handler(towar_do_zamowienia, ilosc_zamawiana)
    else:
        st.info("Brak towarów w magazynie, nie można złożyć zamówienia.")

with col_manage:
    # --- DODAWANIE TOWARU (CREATE) ---
    st.header("➕ Dodaj / ➖ Usuń Towar")

    tab_add, tab_remove = st.tabs(["Dodaj Towar", "Usuń Towar"])
    
    with tab_add:
        nowy_towar = st.text_input("Nazwa Towaru", key="input_towar_add", value="")
        col_a, col_b = st.columns(2)
        with col_a:
            nowa_ilosc = st.number_input("Ilość", min_value=1, value=1, step=1, key="input_ilosc_add")
        with col_b:
            nowa_cena = st.number_input("Cena jednostkowa (PLN)", min_value=0.01, value=100.00, step=0.50, format="%.2f", key="input_cena_add")
        
        if st.button("Dodaj Nowy Towar do Magazynu", key="submit_add"):
            dodaj_towar_handler(nowy_towar, nowa_ilosc, nowa_cena)
            
    with tab_remove:
        if st.session_state.magazyn:
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


# --- WYŚWIETLANIE HISTORII ZAMÓWIEŃ (SIDEBAR) ---
if st.session_state.zamowienia:
    st.sidebar.markdown("---")
    st.sidebar.subheader("📜 Ostatnie Zamówienia")
    
    df_zamowienia = pd.DataFrame(st.session_state.zamowienia)
    # Wyświetlamy tylko ostatnie 5 zamówień, sortując po dacie
    df_zamowienia = df_zamowienia.sort_values(by="Data", ascending=False).head(5)
    
    st.sidebar.dataframe(
        df_zamowienia[['Data', 'Towar', 'Ilość', 'Wartość']],
        hide_index=True,
        use_container_width=True
    )
    st.sidebar.markdown(f"**Łączna wartość z historii:** **{pd.DataFrame(st.session_state.zamowienia)['Wartość'].sum():,.2f}** PLN")
else:
    st.sidebar.info("Brak złożonych zamówień w historii.")

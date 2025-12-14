import streamlit as st
import pandas as pd

# Ustawienie konfiguracji strony
st.set_page_config(
    page_title="Prosty Magazyn",
    layout="wide"
)

# --- Użycie st.session_state do przechowywania listy ---
# Inicjalizacja magazynu w stanie sesji, jeśli nie istnieje.
if 'magazyn' not in st.session_state:
    st.session_state.magazyn = [
        {"Towar": "Laptop Pro", "Ilość": 5, "Cena jednostkowa": 4500.00},
        {"Towar": "Monitor 27'", "Ilość": 12, "Cena jednostkowa": 1200.00},
        {"Towar": "Klawiatura Mechaniczna", "Ilość": 25, "Cena jednostkowa": 350.00}
    ]

# --- Funkcje Logiki Magazynu (CRUD na liście) ---

def dodaj_towar_handler(towar, ilosc, cena):
    """Obsługa dodawania towaru i konwersji typów."""
    if not towar:
        st.error("Proszę podać nazwę towaru.")
        return

    try:
        ilosc = int(ilosc)
        cena = float(cena)
    except ValueError:
        st.error("Ilość musi być liczbą całkowitą, a Cena musi być liczbą zmiennoprzecinkową.")
        return

    nowy_towar = {"Towar": towar, "Ilość": ilosc, "Cena jednostkowa": cena}
    st.session_state.magazyn.append(nowy_towar)
    st.success(f"Dodano: **{towar}** (Ilość: {ilosc})")
    st.rerun() # Poprawne odświeżenie po dodaniu

def usun_towar_handler(indeks):
    """Obsługa usuwania towaru i odświeżania."""
    if 0 <= indeks < len(st.session_state.magazyn):
        nazwa_usunieta = st.session_state.magazyn[indeks]['Towar']
        del st.session_state.magazyn[indeks]
        st.warning(f"Usunięto towar: **{nazwa_usunieta}**")
        st.rerun() # Poprawne odświeżenie po usunięciu
    else:
        st.error("Wystąpił błąd podczas usuwania. Niepoprawny indeks.")


# --- Interfejs Użytkownika Streamlit ---

st.title("📦 Prosty Magazyn (Demo Streamlit)")
st.caption("Dane są przechowywane w pamięci sesji i zostaną zresetowane po zamknięciu przeglądarki.")

st.header("Lista Aktualnych Towarów")

if st.session_state.magazyn:
    # 1. WYŚWIETLANIE MAGAZYNU (READ)
    df_magazyn = pd.DataFrame(st.session_state.magazyn)
    df_magazyn['Wartość'] = df_magazyn['Ilość'] * df_magazyn['Cena jednostkowa']
    
    st.dataframe(df_magazyn, use_container_width=True, hide_index=True)
    
    st.markdown(f"**Łączna wartość magazynu:** **{df_magazyn['Wartość'].sum():,.2f}** PLN")
else:
    st.info("Magazyn jest obecnie pusty.")

st.divider()

# --- SEKCJA MODYFIKACJI ---
col_add, col_remove = st.columns(2)

with col_add:
    # --- DODAWANIE TOWARU (CREATE) ---
    st.header("➕ Dodaj Nowy Towar")

    # Użycie zwykłych widżetów zamiast formularza
    nowy_towar = st.text_input("Nazwa Towaru", key="input_towar_add", value="")
    col_a, col_b = st.columns(2)
    with col_a:
        nowa_ilosc = st.number_input("Ilość", min_value=1, value=1, step=1, key="input_ilosc_add")
    with col_b:
        nowa_cena = st.number_input("Cena jednostkowa (PLN)", min_value=0.01, value=100.00, step=0.50, format="%.2f", key="input_cena_add")
    
    # Przycisk wywołujący funkcję obsługującą dodawanie
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
        
        # Wyciągamy indeks z wybranego stringa
        indeks_do_usuniecia = int(wybrany_do_usuniecia_str.split(":")[0])

        # Przycisk wywołujący funkcję obsługującą usuwanie
        if st.button("Usuń wybrany Towar", key="submit_remove", help="Spowoduje trwałe usunięcie całej pozycji z magazynu"):
            usun_towar_handler(indeks_do_usuniecia)
    else:
        st.info("Brak towarów do usunięcia.")

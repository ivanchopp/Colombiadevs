"""Selector de rol del Panel 2. Spec: PD4."""
import streamlit as st

ROLES = ("Persona de Finanzas", "Senior de Finanzas")


def rol_actual() -> str:
    return st.sidebar.selectbox("Rol", ROLES)

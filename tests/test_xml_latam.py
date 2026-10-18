"""EA12: facturas electrónicas XML de otros países de Latinoamérica (el CFDI de México es EA11, en test_cfdi.py). Sin red, sin clave, datos ficticios."""
from datetime import date
from decimal import Decimal

import pytest

from acta.estado import facturas_por_estado
from agents import archivo, flujo, segunda_lectura, xml_factura

# Un ejemplo mínimo y ficticio por formato, con su lectura esperada.
CFDI = b"""<?xml version="1.0" encoding="UTF-8"?>
<cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/4" Version="4.0" TipoDeComprobante="I" Serie="FACT" Folio="2026001"
  SubTotal="9600" Total="11136.0" Moneda="MXN">
  <cfdi:Emisor Rfc="TAV120405H87" Nombre="Tecnolog\xc3\xada Avanzada S.A. de C.V." RegimenFiscal="601"/>
  <cfdi:Receptor Rfc="EMP990101AAA" Nombre="CLIENTE DE PRUEBA"/>
</cfdi:Comprobante>"""

SRI = b"""<?xml version="1.0" encoding="UTF-8"?>
<factura id="comprobante" version="1.1.0">
  <infoTributaria><razonSocial>Tecnolog\xc3\xada Quite\xc3\xb1a S.A.</razonSocial><ruc>1790012345001</ruc>
    <claveAcceso>1410202601179001234500110010010000001231234567811</claveAcceso>
    <estab>001</estab><ptoEmi>001</ptoEmi><secuencial>000000123</secuencial></infoTributaria>
  <infoFactura><fechaEmision>14/10/2026</fechaEmision><totalSinImpuestos>500.00</totalSinImpuestos>
    <importeTotal>540.00</importeTotal><moneda>DOLAR</moneda></infoFactura>
</factura>"""

CFE = b"""<?xml version="1.0" encoding="UTF-8"?>
<ns0:CFE xmlns:ns0="http://cfe.dgi.gub.uy" version="1.0"><ns0:eFact><ns0:Encabezado>
  <ns0:IdDoc><ns0:TipoCFE>111</ns0:TipoCFE><ns0:Serie>A</ns0:Serie><ns0:Nro>1234</ns0:Nro>
    <ns0:FchEmis>2026-10-14</ns0:FchEmis><ns0:FchVenc>2026-10-30</ns0:FchVenc></ns0:IdDoc>
  <ns0:Emisor><ns0:RUCEmisor>210000000013</ns0:RUCEmisor><ns0:RznSoc>Servicios del Plata S.A.</ns0:RznSoc></ns0:Emisor>
  <ns0:Totales><ns0:TpoMoneda>UYU</ns0:TpoMoneda><ns0:MntTotal>12200.00</ns0:MntTotal><ns0:MntPagar>12200.00</ns0:MntPagar></ns0:Totales>
</ns0:Encabezado></ns0:eFact></ns0:CFE>"""

NFE = b"""<?xml version="1.0" encoding="UTF-8"?>
<nfeProc xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00"><NFe><infNFe Id="NFe00000000000000000000000000000000000000000000" versao="4.00">
  <ide><serie>1</serie><nNF>4567</nNF><dhEmi>2026-10-14T10:00:00-03:00</dhEmi></ide>
  <emit><CNPJ>00000000000191</CNPJ><xNome>Comercio Paulista Ltda.</xNome></emit>
  <dest><CNPJ>00000000000272</CNPJ><xNome>CLIENTE DE PRUEBA</xNome></dest>
  <total><ICMSTot><vProd>3000.00</vProd><vNF>3150.75</vNF></ICMSTot></total>
  <cobr><dup><nDup>001</nDup><dVenc>2026-11-13</dVenc><vDup>3150.75</vDup></dup></cobr>
</infNFe></NFe></nfeProc>"""

DTE = """<?xml version="1.0" encoding="ISO-8859-1"?>
<DTE version="1.0"><Documento ID="F123T33"><Encabezado>
  <IdDoc><TipoDTE>33</TipoDTE><Folio>123</Folio><FchEmis>2026-10-14</FchEmis><FchVenc>2026-11-13</FchVenc></IdDoc>
  <Emisor><RUTEmisor>76000000-0</RUTEmisor><RznSoc>Distribuidora Andina SpA</RznSoc></Emisor>
  <Receptor><RUTRecep>77000000-0</RUTRecep><RznSocRecep>CLIENTE DE PRUEBA</RznSocRecep></Receptor>
  <Totales><MntNeto>100000</MntNeto><IVA>19000</IVA><MntTotal>119000</MntTotal></Totales>
</Encabezado></Documento></DTE>""".encode("iso-8859-1")

COSTA_RICA = b"""<?xml version="1.0" encoding="UTF-8"?>
<FacturaElectronica xmlns="https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.4/facturaElectronica">
  <NumeroConsecutivo>00100001010000000123</NumeroConsecutivo>
  <Emisor><Nombre>Servicios Ticos S.A.</Nombre><Identificacion><Tipo>02</Tipo><Numero>3101000000</Numero></Identificacion></Emisor>
  <Receptor><Nombre>CLIENTE DE PRUEBA</Nombre></Receptor>
  <ResumenFactura><TotalComprobante>565000.00000</TotalComprobante></ResumenFactura>
</FacturaElectronica>"""

SIFEN = b"""<?xml version="1.0" encoding="UTF-8"?>
<rDE xmlns="http://ekuatia.set.gov.py/sifen/xsd"><DE Id="01800000000001001000012322026101410000000000">
  <gTimb><iTiDE>1</iTiDE><dNumTim>12345678</dNumTim><dEst>001</dEst><dPunExp>001</dPunExp><dNumDoc>0000123</dNumDoc></gTimb>
  <gDatGralOpe><gOpeCom><cMoneOpe>PYG</cMoneOpe></gOpeCom>
    <gEmis><dRucEm>80000000</dRucEm><dDVEmi>1</dDVEmi><dNomEmi>Comercial Guarani S.A.</dNomEmi></gEmis></gDatGralOpe>
  <gDtipDE><gCamCond><gPagCred><gCuotas><dVencCuo>2026-11-13</dVencCuo></gCuotas></gPagCred></gCamCond></gDtipDE>
  <gTotSub><dTotGralOpe>1500000</dTotGralOpe></gTotSub>
</DE></rDE>"""

SUNAT = b"""<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
  xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
  xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
  <cbc:UBLVersionID>2.1</cbc:UBLVersionID><cbc:ID>F001-00000123</cbc:ID><cbc:IssueDate>2026-10-14</cbc:IssueDate>
  <cbc:DocumentCurrencyCode>PEN</cbc:DocumentCurrencyCode>
  <cac:AccountingSupplierParty><cac:Party>
    <cac:PartyIdentification><cbc:ID schemeID="6">20100000001</cbc:ID></cac:PartyIdentification>
    <cac:PartyLegalEntity><cbc:RegistrationName>Servicios Limenos S.A.C.</cbc:RegistrationName></cac:PartyLegalEntity>
  </cac:Party></cac:AccountingSupplierParty>
  <cac:PaymentTerms><cbc:ID>FormaPago</cbc:ID><cbc:PaymentDueDate>2026-11-13</cbc:PaymentDueDate></cac:PaymentTerms>
  <cac:LegalMonetaryTotal><cbc:PayableAmount currencyID="PEN">2360.00</cbc:PayableAmount></cac:LegalMonetaryTotal>
</Invoice>"""

ESPERADO = [
    (SRI, "SRI (Ecuador)", "Tecnología Quiteña S.A.", "001-001-000000123", "540.00", "USD", None, "1790012345001"),
    (CFE, "CFE (Uruguay)", "Servicios del Plata S.A.", "A-1234", "12200.00", "UYU", "2026-10-30", "210000000013"),
    (NFE, "NF-e (Brasil)", "Comercio Paulista Ltda.", "1-4567", "3150.75", "BRL", "2026-11-13", "00000000000191"),
    (DTE, "DTE (Chile)", "Distribuidora Andina SpA", "123", "119000", "CLP", "2026-11-13", "76000000-0"),
    (COSTA_RICA, "Factura electrónica (Costa Rica)", "Servicios Ticos S.A.", "00100001010000000123", "565000.00000",
     "CRC", None, "3101000000"),
    (SIFEN, "SIFEN (Paraguay)", "Comercial Guarani S.A.", "001-001-0000123", "1500000", "PYG", "2026-11-13", "80000000-1"),
    (SUNAT, "UBL 2.1", "Servicios Limenos S.A.C.", "F001-00000123", "2360.00", "PEN", "2026-11-13", "20100000001"),
]


@pytest.mark.parametrize("datos,formato,benef,numero,monto,moneda,vence,ident", ESPERADO, ids=[e[1] for e in ESPERADO])
def test_ea12_2_lectura_estructural_de_cada_formato(datos, formato, benef, numero, monto, moneda, vence, ident):
    r = xml_factura.leer(datos)
    assert (r["formato"], r["beneficiario"], r["numero"], r["monto"], r["moneda"], r["vence"], r["id_tributaria"]) == \
        (formato, benef, numero, Decimal(monto), moneda, vence, ident)
    assert r["dudosos"] == ([] if vence else ["vence"])                 # EA12.5
    assert "nit_dv" not in r or r["nit_dv"] is None                     # EA12.9: solo el NIT colombiano


@pytest.mark.parametrize("datos", [e[0] for e in ESPERADO], ids=[e[1] for e in ESPERADO])
def test_ea12_6_la_segunda_lectura_por_patrones_lee_lo_mismo(datos):
    tipo = archivo.validar("f.xml", datos)
    texto = archivo.extraer_texto(tipo, datos)
    lectura = xml_factura.leer(datos)
    p = segunda_lectura.leer(texto)
    for campo in ("beneficiario", "monto", "moneda", "id_tributaria"):
        assert p[campo] == lectura[campo], campo
    assert p["vence"] == (date.fromisoformat(lectura["vence"]) if lectura["vence"] else None)
    estado, difieren = segunda_lectura.comparar(lectura, texto)
    assert difieren == (["vence"] if lectura["vence"] is None else []) and estado == ("no_coincide" if difieren else "coincide")


def test_ea12_6_si_el_texto_dice_otro_monto_no_coincide():
    lectura = xml_factura.leer(CFE)
    lectura["monto"] = Decimal("99999.00")
    assert segunda_lectura.comparar(lectura, CFE.decode())[1] == ["monto"]


@pytest.mark.parametrize("datos,viejo", [(CFE, b"<ns0:MntPagar>12200.00"), (CFDI, b'Total="11136.0'), (SUNAT, b'"PEN">2360.00')],
                         ids=["CFE", "CFDI", "UBL"])
def test_ea12_3_decimales_estrictos_en_las_dos_lecturas(datos, viejo):
    nuevo = viejo.replace(viejo.split(b">")[-1] if b">" in viejo else viejo.split(b'"')[-1], b"640.125")
    datos = datos.replace(viejo, nuevo)
    assert xml_factura.leer(datos)["monto"] == Decimal("640.125")
    assert segunda_lectura.leer(datos.decode("utf-8"))["monto"] == Decimal("640.125")    # no 640125
    assert xml_factura.leer(datos.replace(b"640.125", b"11.136,00"))["monto"] is None


def test_ea12_3_el_atributo_subtotal_no_se_confunde_con_total():
    datos = CFDI.replace(b'Total="11136.0"', b"")
    assert xml_factura.leer(datos)["monto"] is None and segunda_lectura.leer(datos.decode())["monto"] is None


def test_ea12_4_moneda_invalida_queda_sin_leer():
    r = xml_factura.leer(SRI.replace(b"DOLAR", b"PESOS FUERTES"))
    assert r["moneda"] is None and "moneda" in r["dudosos"]
    assert xml_factura.leer(COSTA_RICA.replace(b"<ResumenFactura>", b"<ResumenFactura><CodigoTipoMoneda>"
                                               b"<CodigoMoneda>USD</CodigoMoneda></CodigoTipoMoneda>"))["moneda"] == "USD"


def test_ea12_1_autorizacion_del_sri_se_desenvuelve():
    interno = SRI.decode().replace('<?xml version="1.0" encoding="UTF-8"?>', "")
    envuelto = (f"<autorizacion><estado>AUTORIZADO</estado><comprobante><![CDATA[{interno}]]></comprobante>"
                "</autorizacion>").encode()
    assert xml_factura.leer(envuelto)["numero"] == "001-001-000000123"
    assert segunda_lectura.leer(envuelto.decode())["monto"] == Decimal("540.00")


def test_ea12_8_doctype_dentro_de_la_autorizacion_se_rechaza():
    peligro = b'<autorizacion><comprobante><![CDATA[<!DOCTYPE x [<!ENTITY a "b">]><factura/>]]></comprobante></autorizacion>'
    with pytest.raises(xml_factura.XmlInvalido, match="entidades"):
        xml_factura.leer(peligro)


def test_ea12_8_iso_8859_1_y_xml_sin_declaracion_se_aceptan():
    assert archivo.validar("dte.xml", DTE) == "xml"
    assert "Distribuidora Andina" in archivo.extraer_texto("xml", DTE)
    sin_declaracion = CFDI.split(b"?>", 1)[1].lstrip()
    assert archivo.validar("cfdi.xml", sin_declaracion) == "xml"
    with pytest.raises(archivo.ArchivoRechazado):
        archivo.validar("cfdi.txt", sin_declaracion)                  # contenido XML con extensión txt


@pytest.fixture(autouse=True)
def sin_clave(monkeypatch):
    for v in ("ANTHROPIC_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY", "PROVEEDOR_IA", "ENTRADA_MODO"):
        monkeypatch.delenv(v, raising=False)


def decision(almacen, sala, fid):
    return facturas_por_estado(almacen.filas(sala))[fid].decision


def test_ea12_7_xml_de_formato_desconocido_se_lee_como_texto_y_se_escala(almacen, sala):
    ar = (b'<?xml version="1.0" encoding="UTF-8"?><comprobanteAR><cuit>30000000007</cuit>'
          b"<razonSocial>Servicios Porte\xc3\xb1os S.A.</razonSocial><ptoVta>00001</ptoVta><nro>00000123</nro>"
          b"<impTotal>1210.00</impTotal><moneda>PES</moneda><cae>70000000000000</cae></comprobanteAR>")
    with pytest.raises(xml_factura.FormatoDesconocido):
        xml_factura.leer(ar)
    e = flujo.recibir(almacen, sala, "ar.xml", ar)                     # no se rechaza
    assert e["modo"] != "xml" and e["segunda"] == "no_disponible" and e["lectura"]["formato"] == "XML no reconocido"
    while e["estado"] == "recibida" and e["pendientes"]:
        e = flujo.responder(almacen, sala, e["factura_id"], "no sé")
    assert decision(almacen, sala, e["factura_id"]) != "PAGAR"


def test_ea12_sri_no_llama_a_la_ia_y_sin_vencimiento_nunca_se_paga_solo(almacen, sala):
    class Bomba:
        def __getattr__(self, _):
            raise AssertionError("un XML reconocido no debe usar la IA")
    e = flujo.recibir(almacen, sala, "sri.xml", SRI, cliente=Bomba())
    assert e["modo"] == "xml" and e["pendientes"] == ["vence"]          # EA12.5: se le pregunta al proveedor
    e = flujo.responder(almacen, sala, e["factura_id"], "2026-10-30")
    assert decision(almacen, sala, e["factura_id"]) != "PAGAR"

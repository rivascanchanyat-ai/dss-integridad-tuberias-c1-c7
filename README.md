# DSS DRBI - IOWs - Bayes

Sistema de soporte a decisiones para integridad de tuberías.

Arquitectura funcional:

C1 Datos
→ C2 IOW / Umbrales
→ C3 Actualización Bayesiana
→ C4 DRBI
→ Riesgo / RUL / Prioridad

La base incluida corresponde a datos sintéticos de desarrollo académico.

La aplicación permite:
- consultar líneas y tramos;
- registrar nuevas líneas;
- registrar nuevos tramos homogéneos;
- consultar IOW;
- visualizar PoF Bayesiana;
- consultar resultados DRBI;
- revisar inspecciones UT;
- preparar futuras integraciones DCS / LIMS / IIoT.

La versión industrial deberá utilizar PostgreSQL/TimescaleDB
y mecanismos corporativos de autenticación, auditoría y respaldo.

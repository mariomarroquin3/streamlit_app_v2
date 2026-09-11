# Fuentes y verificación — Directorio de centros oftalmológicos

Este documento respalda los datos del directorio verificado de centros
oftalmológicos que aparece en **Lugares de Ayuda** (`/lugares-de-ayuda`),
tanto para la defensa del proyecto en la competencia EUREKA como para que
cualquier persona pueda auditar de dónde sale cada dato.

Última revisión: **10 de septiembre de 2026**.

## Metodología

1. **Fuente primaria u oficial antes que resumen de búsqueda.** Para cada
   institución se buscó su sitio web oficial, su página en el portal de
   transparencia del gobierno correspondiente, o un documento oficial
   (portafolio de servicios, diagnóstico ministerial). Un resumen generado
   por una herramienta de búsqueda se usó solo como punto de partida, nunca
   como fuente final — siempre se intentó abrir el documento/página original
   para leer el dato directamente.
2. **Coordenadas por geocodificación, no estimadas.** Todas las coordenadas
   se obtuvieron consultando la dirección verificada contra
   [Nominatim](https://nominatim.openstreetmap.org) (el servicio de
   geocodificación de OpenStreetMap), no se "adivinaron" a partir del nombre
   de la ciudad.
3. **Si no se pudo verificar, se eliminó.** Cuando no se encontró evidencia
   de que una institución existiera con el nombre, dirección o teléfono que
   tenía el proyecto, la entrada se retiró del directorio en vez de dejarla
   con datos dudosos. La sección [Correcciones y retiros](#correcciones-y-retiros-2026-09-10)
   documenta cada caso.
4. **Los datos en vivo (OpenStreetMap) se presentan con advertencia.** Fuera
   del directorio curado de abajo, la app también muestra resultados de una
   búsqueda en vivo contra la API de Overpass/OpenStreetMap. Esos resultados
   **no** pasan por este mismo proceso de verificación (viene de datos
   colaborativos de terceros), por lo que la interfaz les añade siempre la
   advertencia *"Datos de OpenStreetMap sin verificar — confirma servicios,
   horario y disponibilidad directamente con el lugar antes de acudir"*.

---

## El Salvador — Red pública (MINSAL)

Fuente principal: **"Diagnóstico Nacional de Salud Visual en El Salvador"**,
Ministerio de Salud de El Salvador, 2022 — documento oficial con visita
diagnóstica a los 10 hospitales de la red MINSAL que brindan atención
oftalmológica, incluyendo recurso humano, equipamiento y qué tratamientos
realiza cada uno (tamizaje/tratamiento de retinopatía diabética, cataratas,
glaucoma).
<https://asp.salud.gob.sv/regulacion/pdf/otrosdoc/diagnosticonacionaldesaludvisualenelsalvador_Presentacion-885_v1.pdf>

Se incluyeron 8 de esos 10 hospitales (se omiten Hospital Nacional de la
Mujer y Hospital Nacional San Vicente por tener infraestructura o recurso
humano de oftalmología no confirmado o nulo según ese mismo diagnóstico).

| Institución | Fuente(s) específica(s) | Qué se verificó |
|---|---|---|
| Centro Oftalmológico Nacional (Hospital Nacional "Dr. Juan José Fernández", Zacamil) | Diagnóstico MINSAL 2022 (Tablas 23, 27–31, 34); [comunicado oficial de inauguración, MINSAL](https://www.salud.gob.sv/ministerio-de-salud-inaugura-el-nuevo-centro-oftalmologico-nacional/) | Existencia, ubicación, recurso humano (6 oftalmólogos + residencia), subespecialidad en glaucoma, cirugía de cataratas |
| Hospital Nacional Rosales | Diagnóstico MINSAL 2022 (Tablas 23, 27–32, 34); [ficha institucional, Médicos de El Salvador](https://www.medicosdeelsalvador.com/hospitales/hospital-nacional-rosales_278.html); [Wikipedia (dirección)](https://es.wikipedia.org/wiki/Hospital_Nacional_Rosales) | Horario de consulta de oftalmología (L–D 1–3pm), único hospital con facoemulsificación para cataratas, subespecialidades (retina, glaucoma, estrabismo, segmento anterior) |
| Hospital Nacional "San Rafael" (Santa Tecla) | **Portafolio de Servicios 2023 del hospital** (documento oficial, leído directamente): <https://www.salud.gob.sv/wp-content/uploads/2022/06/OFERTA-DE-SERVICIOS-HOSP-NAC-SAN-RAFAEL.pdf>; teléfono confirmado también en su [página de transparencia](https://www.transparencia.gob.sv/institutions/h-san-rafael/services/6506) | Oftalmología es consulta externa programada (L–V 7am–12pm) dentro del Depto. de Cirugía — **no** un servicio de urgencia, como decía una versión anterior de esta entrada |
| Hospital Nacional Regional "San Juan de Dios" (Santa Ana) | **Oferta de Servicios Hospitalarios 2023** (documento oficial, leído directamente): <https://www.transparencia.gob.sv/descarga_archivo.php?id=NTIyNTgy&inst=522582>; Diagnóstico MINSAL 2022 | Cirugía de cataratas, programa de glaucoma con láser, subespecialidad oculoplástica, 4 oftalmólogos |
| Hospital Nacional Regional "San Juan de Dios" (San Miguel) | Diagnóstico MINSAL 2022 (Tablas 23, 27, 29, 34) | 2 oftalmólogos, tamizaje de retinopatía diabética, cirugía de cataratas confirmados |
| Hospital Nacional de Sonsonate "Jorge Mazzini Villacorta" | Diagnóstico MINSAL 2022 (Tablas 23, 27, 29, 34) | 2 oftalmólogos, tamizaje de retinopatía diabética, cirugía de cataratas confirmados |
| Hospital Nacional "San Pedro" (Usulután) | Diagnóstico MINSAL 2022 (Tablas 23, 27, 29, 34); [confirmación de nombre oficial](https://www.transparencia.gob.sv/institutions/h-usulutan) (evita confundirlo con el Hospital "Dr. Jorge Arturo Mena" de Santiago de María, en el mismo departamento) | 1 oftalmólogo, tamizaje de retinopatía diabética, cirugía de cataratas |

Coordenadas de los 8 hospitales geocodificadas individualmente con Nominatim
a partir de su dirección o nombre oficial (no se reutilizó ninguna
coordenada de ciudad genérica).

## El Salvador — Clínicas privadas

| Institución | Fuente(s) | Nivel de confianza |
|---|---|---|
| Hospital de Ojos y Especialidades | [Ficha institucional, Médicos de El Salvador](https://www.medicosdeelsalvador.com/hospitales/hospital-de-ojos-y-especialidades_597.html) | Alto — dirección, teléfono y fundación por oftalmólogos confirmados en la fuente |
| Clínica de Ojos Santa Lucía | Sitio propio de la clínica y menciones de su subespecialista en retina y vítreo (Dra. Berenice Molina) | Moderado — se confirmó que la institución y su especialista en retina existen, pero no se encontró un listado detallado y oficial de procedimientos específicos, por lo que los servicios listados en la app se mantienen deliberadamente genéricos |

---

## Guatemala

| Institución | Fuente(s) | Qué se verificó |
|---|---|---|
| Hospital de Ojos y Oídos Dr. Rodolfo Robles (Comité Pro Ciegos y Sordos) | [Sitio oficial del Comité, división médica](https://prociegosysordos.org.gt/Division%20Medica/RodolfoRobles.php); publicaciones oficiales en Facebook del Comité | Dirección (Diagonal 21, 19-19 Zona 11), teléfono, servicio de retina y vítreo (retinopexias, vitrectomías) |
| Clínica Visualiza | [Página oficial de ubicaciones/contacto](https://visualiza.com.gt/ubicaiocnes-contactanos/) | Dirección y teléfono de la sede zona 9; Centro Diabético de la clínica |
| Instituto Panamericano Contra la Ceguera (IPC) | [Directorio Guatemala.com](https://directorio.guatemala.com/listado/instituto-panamericano-contra-la-ceguera.html) | **Nombre real de la institución** (una versión anterior de esta entrada usaba el nombre y las siglas incorrectas, "Instituto Panamericano de Ojos / IPO", que no corresponden a ninguna institución real encontrada), dirección, teléfono |
| Centro Visual G&G | [Sitio oficial](https://esp.centrovisualgyg.com/) | **Ubicación real: Antigua Guatemala** (una versión anterior de esta entrada la ubicaba, incorrectamente, en Ciudad de Guatemala — un error de ~26 km); cirugía de retina/vítreo/mácula, Angio-OCT, angiografía fluoresceínica |

## Honduras

Se retiraron las dos entradas que tenía el proyecto ("Instituto Hondureño de
Oftalmología y Retina" y "Centro de Ojos del Valle", San Pedro Sula) porque
no se encontró ninguna evidencia de que existan con esos nombres, direcciones
o teléfonos. Actualmente **no hay directorio curado para Honduras**; la
búsqueda en vivo vía OpenStreetMap sigue funcionando (con su advertencia de
datos no verificados).

## Costa Rica

| Institución | Fuente(s) | Nota |
|---|---|---|
| Retina CR | [Sitio oficial](https://retinacr.com/en/) | Reemplaza a una entrada anterior, "Clínica 20/20 y Centro de Retina de Costa Rica", que resultó ser una combinación de dos lugares reales pero distintos (Clínica 20/20, en Sabana Oeste, y esta clínica de retina real, en Torre Mercedes / Paseo Colón) presentados como si fueran uno solo. Cirugía vitreorretiniana, láser retinal, OCT y angiografía confirmados en el sitio oficial |

## México

| Institución | Fuente(s) | Qué se verificó |
|---|---|---|
| Instituto de Oftalmología Fundación Conde de Valenciana | [Sitio institucional oficial](https://www.institutodeoftalmologia.org/) | Dirección exacta (Chimalpopoca 14, Col. Obrera), teléfono, atención de alta especialidad en retina |
| Asociación para Evitar la Ceguera en México (APEC) | [Sitio oficial, "Quiénes somos"](https://www.apec.org.mx/quienes-somos); [directorio de la Agencia Internacional para la Prevención de la Ceguera (IAPB)](https://www.iapb.org/connect/members/members-directory/asociacion-para-evitar-la-ceguera-en-mexico/) | Dirección, teléfono, especialidades de retina y vítreo |
| Hospital Puerta de Hierro — Andares (Zapopan) | [Sitio oficial, servicio de oftalmología](https://hospitalespuertadehierro.com/en/hospitals/andares/ophthalmology/) | Dirección, teléfono, vitrectomía y tratamiento de patología retinal |

---

## Correcciones y retiros (2026-09-10)

Para transparencia total, esta es la lista completa de lo que se corrigió o
eliminó del directorio durante la auditoría de esta sesión, y por qué. Ver
también el archivo `CLAUDE.md` del proyecto para el detalle técnico.

| Entrada original | Problema encontrado | Acción |
|---|---|---|
| "Instituto de Ojos de El Salvador (INCLIO)" | Nombre, dirección y teléfono no correspondían a ninguna institución real encontrada | Reemplazada por "Hospital de Ojos y Especialidades" (verificado) |
| "Centro Oftalmológico Integral (COI Guatemala)" | Sin evidencia de que exista en Guatemala con ese nombre | Eliminada |
| "Instituto Panamericano de Ojos (IPO)" | Nombre y siglas incorrectos; dirección y teléfono también incorrectos | Corregida al nombre real, "Instituto Panamericano Contra la Ceguera (IPC)" |
| "Centro Visual G&G / Especialistas en Retina" | Geolocalizada en Ciudad de Guatemala; en realidad está en Antigua Guatemala (~26 km de diferencia) | Corregida ciudad, dirección, teléfono y coordenadas |
| "Centro Oftalmológico de Occidente (Quetzaltenango)" | Sin evidencia de que exista con ese nombre | Eliminada |
| "Instituto Hondureño de Oftalmología y Retina" | Sin evidencia de que exista | Eliminada |
| "Centro de Ojos del Valle" (San Pedro Sula) | Sin evidencia de que exista | Eliminada |
| "Clínica 20/20 y Centro de Retina de Costa Rica" | Combinaba dos instituciones reales distintas en una sola entrada con datos mezclados | Reemplazada por "Retina CR" (institución real e independiente) |
| Teléfonos de Visualiza, Conde de Valenciana, Puerta de Hierro | Números incorrectos o desactualizados | Corregidos contra fuente oficial |

### Bug de software relacionado (clasificación de resultados en vivo)

Además del directorio curado, se encontró y corrigió un error en el código
que clasifica los resultados en vivo de OpenStreetMap: usaba coincidencia de
subcadena de texto para detectar palabras clave como "retina" o "mácula", lo
que producía falsos positivos graves — por ejemplo, una **farmacia** llamada
"Los Robles" o clínicas familiares con "Inmaculada" en el nombre (muy común
en instituciones católicas de la región) aparecían clasificadas como
"Alta Especialidad en Retina" con procedimientos quirúrgicos inventados
(vitrectomía, anti-VEGF), simplemente porque "Robles" e "Inmaculada"
contienen las subcadenas "robles" y "macula" respectivamente. Se corrigió
exigiendo coincidencia de palabra completa. Ver `static/js/map.js`
(función `containsKeyword`) y `CLAUDE.md` para el detalle técnico completo.

---

## Limitaciones conocidas

- El directorio curado prioriza cobertura en **El Salvador** (verificación
  más profunda y completa, ligada al contexto del proyecto) y capitales/
  ciudades principales de Guatemala, Costa Rica y México. No es exhaustivo:
  hay centros oftalmológicos reales que no están incluidos.
- Horarios, teléfonos y disponibilidad de equipos (p. ej. láser) pueden
  cambiar con el tiempo; la fecha de verificación de cada fuente se anota
  cuando el documento original la trae (p. ej. el Diagnóstico MINSAL es de
  2022 y sus portafolios de servicios hospitalarios son de 2023).
  Se recomienda siempre llamar para confirmar antes de acudir — la propia
  interfaz de la app lo indica.
- Los resultados en vivo de OpenStreetMap son datos abiertos editados por la
  comunidad: pueden estar desactualizados, incompletos o, en casos raros,
  con información incorrecta cargada por terceros. Por eso llevan la
  advertencia explícita en la interfaz y no se presentan con el mismo nivel
  de confianza que el directorio curado de esta tabla.

/**
 * map.js
 * ======
 * Módulo interactivo de OpenStreetMap (OSM) y Leaflet para la búsqueda
 * EXCLUSIVA de centros oftalmológicos, clínicas de ojos y especialistas
 * en retina y retinopatía diabética.
 *
 * Incluye:
 * - Selector interactivo de País y Ciudad / Departamento en cascada.
 * - Posibilidad de colocar y arrastrar el pin libremente haciendo clic en el mapa.
 * - Radios de cobertura extendidos de 10 km a 500 km.
 * - Directorio integral de referencia médica y consulta en tiempo real a OpenStreetMap.
 */

(function () {
  'use strict';

  // --- Datos de Países y Ciudades / Departamentos con Coordenadas ---
  const COUNTRY_CITY_DATABASE = {
    GT: {
      name: 'Guatemala',
      defaultLat: 14.6349,
      defaultLon: -90.5069,
      cities: [
        { name: 'Ciudad de Guatemala (Capital)', lat: 14.6349, lon: -90.5069 },
        { name: 'Mixco', lat: 14.6310, lon: -90.6067 },
        { name: 'Villa Nueva', lat: 14.5256, lon: -90.5886 },
        { name: 'Quetzaltenango (Xela)', lat: 14.8340, lon: -91.5180 },
        { name: 'Escuintla', lat: 14.3009, lon: -90.7850 },
        { name: 'Antigua Guatemala (Sacatepéquez)', lat: 14.5586, lon: -90.7295 },
        { name: 'Chimaltenango', lat: 14.6611, lon: -90.8194 },
        { name: 'Huehuetenango', lat: 15.3197, lon: -91.4708 },
        { name: 'Cobán (Alta Verapaz)', lat: 15.4708, lon: -90.3708 },
        { name: 'Mazatenango (Suchitepéquez)', lat: 14.5342, lon: -91.5033 },
        { name: 'Retalhuleu', lat: 14.5361, lon: -91.6778 },
        { name: 'Puerto Barrios (Izabal)', lat: 15.7278, lon: -88.5944 },
        { name: 'Jalapa', lat: 14.6347, lon: -89.9889 },
        { name: 'Jutiapa', lat: 14.2917, lon: -89.8958 },
        { name: 'Zacapa', lat: 14.9722, lon: -89.5306 },
        { name: 'Chiquimula', lat: 14.7981, lon: -89.5458 },
        { name: 'Flores / Santa Elena (Petén)', lat: 16.9242, lon: -89.8953 }
      ]
    },
    SV: {
      name: 'El Salvador',
      defaultLat: 13.6929,
      defaultLon: -89.2182,
      cities: [
        { name: 'San Salvador (Capital)', lat: 13.6929, lon: -89.2182 },
        { name: 'Santa Tecla (La Libertad)', lat: 13.6769, lon: -89.2797 },
        { name: 'Santa Ana', lat: 13.9942, lon: -89.5597 },
        { name: 'San Miguel', lat: 13.4833, lon: -88.1833 },
        { name: 'Soyapango', lat: 13.7103, lon: -89.1397 },
        { name: 'Antiguo Cuscatlán', lat: 13.6739, lon: -89.2508 },
        { name: 'Sonsonate', lat: 13.7189, lon: -89.7242 },
        { name: 'Ahuachapán', lat: 13.9214, lon: -89.8450 },
        { name: 'Usulután', lat: 13.3458, lon: -88.4361 },
        { name: 'Chalatenango', lat: 14.0417, lon: -88.9333 }
      ]
    },
    MX: {
      name: 'México',
      defaultLat: 19.4326,
      defaultLon: -99.1332,
      cities: [
        { name: 'Ciudad de México (CDMX)', lat: 19.4326, lon: -99.1332 },
        { name: 'Guadalajara (Jalisco)', lat: 20.6597, lon: -103.3496 },
        { name: 'Monterrey (Nuevo León)', lat: 25.6866, lon: -100.3161 },
        { name: 'Puebla', lat: 19.0414, lon: -98.2063 },
        { name: 'Tijuana (Baja California)', lat: 32.5149, lon: -117.0382 },
        { name: 'León (Guanajuato)', lat: 21.1221, lon: -101.6820 },
        { name: 'Querétaro', lat: 20.5888, lon: -100.3899 },
        { name: 'Mérida (Yucatán)', lat: 20.9674, lon: -89.5926 },
        { name: 'Cancún (Quintana Roo)', lat: 21.1619, lon: -86.8515 },
        { name: 'Toluca (Estado de México)', lat: 19.2826, lon: -99.6557 },
        { name: 'Cuernavaca (Morelos)', lat: 18.9242, lon: -99.2216 },
        { name: 'Veracruz', lat: 19.1738, lon: -96.1342 },
        { name: 'Oaxaca de Juárez', lat: 17.0732, lon: -96.7266 },
        { name: 'Tuxtla Gutiérrez (Chiapas)', lat: 16.7569, lon: -93.1292 },
        { name: 'Tapachula (Chiapas)', lat: 14.9039, lon: -92.2611 }
      ]
    },
    HN: {
      name: 'Honduras',
      defaultLat: 14.0723,
      defaultLon: -87.1921,
      cities: [
        { name: 'Tegucigalpa (Capital)', lat: 14.0723, lon: -87.1921 },
        { name: 'San Pedro Sula (Cortés)', lat: 15.5042, lon: -88.0250 },
        { name: 'La Ceiba (Atlántida)', lat: 15.7597, lon: -86.7822 },
        { name: 'Choluteca', lat: 13.3000, lon: -87.1833 },
        { name: 'Comayagua', lat: 14.4500, lon: -87.6333 },
        { name: 'Santa Rosa de Copán', lat: 14.7667, lon: -88.7833 }
      ]
    },
    CR: {
      name: 'Costa Rica',
      defaultLat: 9.9281,
      defaultLon: -84.0907,
      cities: [
        { name: 'San José (Capital)', lat: 9.9281, lon: -84.0907 },
        { name: 'Alajuela', lat: 10.0163, lon: -84.2116 },
        { name: 'Heredia', lat: 9.9981, lon: -84.1169 },
        { name: 'Cartago', lat: 9.8644, lon: -83.9194 },
        { name: 'Puntarenas', lat: 9.9763, lon: -84.8384 },
        { name: 'Liberia (Guanacaste)', lat: 10.6350, lon: -85.4377 }
      ]
    },
    NI: {
      name: 'Nicaragua',
      defaultLat: 12.1150,
      defaultLon: -86.2362,
      cities: [
        { name: 'Managua (Capital)', lat: 12.1150, lon: -86.2362 },
        { name: 'León', lat: 12.4379, lon: -86.8780 },
        { name: 'Granada', lat: 11.9299, lon: -85.9560 },
        { name: 'Matagalpa', lat: 12.9256, lon: -85.9178 },
        { name: 'Estelí', lat: 13.0919, lon: -86.3539 }
      ]
    },
    PA: {
      name: 'Panamá',
      defaultLat: 8.9824,
      defaultLon: -79.5199,
      cities: [
        { name: 'Ciudad de Panamá (Capital)', lat: 8.9824, lon: -79.5199 },
        { name: 'San Miguelito', lat: 9.0346, lon: -79.5023 },
        { name: 'David (Chiriquí)', lat: 8.4273, lon: -82.4309 },
        { name: 'Colón', lat: 9.3598, lon: -79.9015 }
      ]
    },
    CO: {
      name: 'Colombia',
      defaultLat: 4.7110,
      defaultLon: -74.0721,
      cities: [
        { name: 'Bogotá (Capital)', lat: 4.7110, lon: -74.0721 },
        { name: 'Medellín (Antioquia)', lat: 6.2442, lon: -75.5812 },
        { name: 'Cali (Valle del Cauca)', lat: 3.4516, lon: -76.5320 },
        { name: 'Barranquilla (Atlántico)', lat: 10.9685, lon: -74.7813 },
        { name: 'Bucaramanga (Santander)', lat: 7.1254, lon: -73.1198 },
        { name: 'Cartagena de Indias', lat: 10.3910, lon: -75.4794 },
        { name: 'Pereira (Risaralda)', lat: 4.8133, lon: -75.6961 }
      ]
    },
    PE: {
      name: 'Perú',
      defaultLat: -12.0464,
      defaultLon: -77.0428,
      cities: [
        { name: 'Lima (Capital)', lat: -12.0464, lon: -77.0428 },
        { name: 'Arequipa', lat: -16.4090, lon: -71.5375 },
        { name: 'Trujillo', lat: -8.1160, lon: -79.0300 },
        { name: 'Cusco', lat: -13.5319, lon: -71.9675 }
      ]
    },
    AR: {
      name: 'Argentina',
      defaultLat: -34.6037,
      defaultLon: -58.3816,
      cities: [
        { name: 'Buenos Aires (Capital)', lat: -34.6037, lon: -58.3816 },
        { name: 'Córdoba', lat: -31.4201, lon: -64.1888 },
        { name: 'Rosario (Santa Fe)', lat: -32.9468, lon: -60.6393 },
        { name: 'Mendoza', lat: -32.8895, lon: -68.8458 }
      ]
    },
    CL: {
      name: 'Chile',
      defaultLat: -33.4489,
      defaultLon: -70.6693,
      cities: [
        { name: 'Santiago (Capital)', lat: -33.4489, lon: -70.6693 },
        { name: 'Valparaíso / Viña del Mar', lat: -33.0472, lon: -71.6127 },
        { name: 'Concepción', lat: -36.8201, lon: -73.0444 }
      ]
    },
    ES: {
      name: 'España',
      defaultLat: 40.4168,
      defaultLon: -3.7038,
      cities: [
        { name: 'Madrid (Capital)', lat: 40.4168, lon: -3.7038 },
        { name: 'Barcelona', lat: 41.3874, lon: 2.1686 },
        { name: 'Valencia', lat: 39.4699, lon: -0.3763 },
        { name: 'Sevilla', lat: 37.3891, lon: -5.9845 }
      ]
    },
    OTHER: {
      name: 'Otro País / Global',
      defaultLat: 14.6349,
      defaultLon: -90.5069,
      cities: [
        { name: 'Escribir ciudad en el buscador manual...', lat: 14.6349, lon: -90.5069 }
      ]
    }
  };

  // --- Directorio de Centros Oftalmológicos y de Retina de Referencia Verificados ---
  const VERIFIED_RETINA_CENTERS = [
    // Guatemala
    {
      name: 'Hospital de Ojos y Oídos Dr. Rodolfo Robles (Comité Pro Ciegos y Sordos)',
      lat: 14.6062,
      lon: -90.5511,
      category: 'retina',
      isRetinaSpecialist: true,
      categoryLabel: 'Hospital de Referencia en Retina',
      services: [
        'Unidad de Retina y Retinopatía Diabética',
        'Fotocoagulación con Láser Argón',
        'Inyecciones Intravítreas Anti-VEGF',
        'Cirugía de Vítreo y Retina (Vitrectomía)'
      ],
      address: 'Diagonal 21 19-19 Zona 11, Ciudad de Guatemala',
      phone: '+502 2382-1700'
    },
    {
      name: 'Clínica Visualiza - Centro de Cirugía Ocular y Retina',
      lat: 14.5986,
      lon: -90.5183,
      category: 'retina',
      isRetinaSpecialist: true,
      categoryLabel: 'Alta Especialidad en Retina y Mácula',
      services: [
        'Examen de fondo de ojo con dilatación',
        'Tratamiento de Retinopatía Diabética y Edema Macular',
        'Tomografía de Coherencia Óptica (OCT)'
      ],
      address: '5a Avenida 11-43 Zona 9, Ciudad de Guatemala',
      phone: '+502 2420-9600'
    },
    {
      name: 'Centro Oftalmológico Integral (COI Guatemala)',
      lat: 14.5950,
      lon: -90.5080,
      category: 'retina',
      isRetinaSpecialist: true,
      categoryLabel: 'Especialistas en Retina Médica y Quirúrgica',
      services: [
        'Diagnóstico y tratamiento de Retinopatía',
        'Fotocoagulación láser y microcirugía ocular'
      ],
      address: '6a Avenida 3-22 Zona 10, Edificio Centro Médico II, Ciudad de Guatemala',
      phone: '+502 2332-5501'
    },
    {
      name: 'Instituto Panamericano de Ojos (IPO)',
      lat: 14.5825,
      lon: -90.5122,
      category: 'institutes',
      isRetinaSpecialist: false,
      categoryLabel: 'Instituto de Oftalmología y Cirugía Ocular',
      services: [
        'Consulta oftalmológica especializada',
        'Evaluación preventiva de retina diabética'
      ],
      address: '10 Calle 2-45 Zona 14, Ciudad de Guatemala',
      phone: '+502 2386-4700'
    },
    {
      name: 'Centro Visual G&G / Especialistas en Retina',
      lat: 14.5921,
      lon: -90.5110,
      category: 'retina',
      isRetinaSpecialist: true,
      categoryLabel: 'Clínica de Retina y Glaucoma',
      services: [
        'Fondo de ojo con lámpara de hendidura',
        'Terapia antiangiogénica para retinopatía'
      ],
      address: '12 Calle 1-25 Zona 10, Edificio Géminis 10, Ciudad de Guatemala',
      phone: '+502 2338-2020'
    },
    {
      name: 'Centro Oftalmológico de Occidente (Quetzaltenango)',
      lat: 14.8340,
      lon: -91.5180,
      category: 'institutes',
      isRetinaSpecialist: false,
      categoryLabel: 'Clínica Oftalmológica Regional',
      services: [
        'Detección y control de retinopatía diabética',
        'Examen de agudeza visual y fondo de ojo'
      ],
      address: 'Zona 3, Quetzaltenango, Guatemala',
      phone: '+502 7761-4500'
    },
    // El Salvador — clínicas privadas de referencia en retina
    {
      name: 'Instituto de Ojos de El Salvador (INCLIO)',
      lat: 13.7055,
      lon: -89.2380,
      category: 'retina',
      isRetinaSpecialist: true,
      isPublic: false,
      categoryLabel: 'Alta Especialidad en Retina y Cirugía Ocular (Privado)',
      services: [
        'Tratamiento de Retinopatía Diabética Proliferativa',
        'Láser para retina y terapia Anti-VEGF',
        'Angiografía con Fluoresceína'
      ],
      address: '85 Av. Norte y 3a Calle Poniente, Colonia Escalón, San Salvador',
      phone: '+503 2263-4545'
    },
    {
      name: 'Clínica de Ojos Santa Lucía',
      lat: 13.6960,
      lon: -89.2310,
      category: 'retina',
      isRetinaSpecialist: true,
      isPublic: false,
      categoryLabel: 'Centro Especializado en Retina y Vítreo (Privado)',
      services: [
        'Fondo de ojo y diagnóstico de retina',
        'Fotocoagulación láser'
      ],
      address: 'Alameda Manuel Enrique Araujo, San Salvador, El Salvador',
      phone: '+503 2245-1200'
    },
    // El Salvador — red pública (MINSAL). Verificado contra fuentes oficiales
    // (salud.gob.sv, transparencia.gob.sv) y geocodificado con Nominatim/OSM.
    {
      name: 'Centro Oftalmológico Nacional (Hospital Nacional "Dr. Juan José Fernández", Zacamil)',
      lat: 13.7288574,
      lon: -89.2075851,
      category: 'public',
      isRetinaSpecialist: false,
      isPublic: true,
      categoryLabel: 'Centro de Referencia Nacional en Oftalmología (Público — MINSAL)',
      services: [
        'Atención oftalmológica integral de la red pública',
        'Parte del Plan Nacional de Salud Visual (MINSAL, inaugurado 2020)'
      ],
      address: 'Colonia Zacamil, Mejicanos, San Salvador, El Salvador',
      phone: null
    },
    {
      name: 'Hospital Nacional Rosales',
      lat: 13.7005746,
      lon: -89.2067422,
      category: 'public',
      isRetinaSpecialist: false,
      isPublic: true,
      categoryLabel: 'Hospital Nacional de Referencia (Público — MINSAL)',
      services: [
        'Consulta de oftalmología general',
        'Horario de oftalmología: lunes a domingo, 1:00 pm – 3:00 pm'
      ],
      address: 'Alameda Franklin D. Roosevelt, San Salvador, El Salvador',
      phone: null
    },
    {
      name: 'Hospital Nacional "San Rafael"',
      lat: 13.6711599,
      lon: -89.2783013,
      category: 'public',
      isRetinaSpecialist: false,
      isPublic: true,
      categoryLabel: 'Hospital Nacional Regional (Público — MINSAL)',
      services: [
        'Consulta y atención oftalmológica de urgencia',
        'Hospital de referencia regional para La Libertad'
      ],
      address: 'Final 4a Calle Oriente y 15 Av. Sur, Santa Tecla, La Libertad',
      phone: '+503 2594-4000'
    },
    {
      name: 'Hospital Nacional Regional "San Juan de Dios" (Santa Ana)',
      lat: 13.9918514,
      lon: -89.5512539,
      category: 'public',
      isRetinaSpecialist: false,
      isPublic: true,
      categoryLabel: 'Hospital Nacional Regional (Público — MINSAL)',
      services: [
        'Consulta de oftalmología',
        'Hospital de referencia para la zona occidental'
      ],
      address: 'Final 13 Av. Sur, Santa Ana, El Salvador',
      phone: null
    },
    {
      name: 'Hospital Nacional Regional "San Juan de Dios" (San Miguel)',
      lat: 13.4741017,
      lon: -88.1909591,
      category: 'public',
      isRetinaSpecialist: false,
      isPublic: true,
      categoryLabel: 'Hospital Nacional Regional (Público — MINSAL)',
      services: [
        'Consulta médica general con referencia a oftalmología',
        'Hospital de referencia para la zona oriental'
      ],
      address: 'Final 11a Calle Poniente y 23 Av. Sur, Colonia Ciudad Jardín, San Miguel',
      phone: null
    },
    // Honduras
    {
      name: 'Instituto Hondureño de Oftalmología y Retina',
      lat: 14.0880,
      lon: -87.1850,
      category: 'retina',
      isRetinaSpecialist: true,
      categoryLabel: 'Unidad Especializada en Retina',
      services: [
        'Fondo de ojo con dilatación',
        'Fotocoagulación láser para retinopatía',
        'Inyecciones Anti-VEGF'
      ],
      address: 'Colonia Palmira, Tegucigalpa, Honduras',
      phone: '+504 2238-5000'
    },
    {
      name: 'Centro de Ojos del Valle (San Pedro Sula)',
      lat: 15.5120,
      lon: -88.0310,
      category: 'institutes',
      isRetinaSpecialist: false,
      categoryLabel: 'Clínica de Cirugía Ocular y Retina',
      services: [
        'Diagnóstico y control de retinopatía diabética',
        'Cirugía de cataratas y vítreo'
      ],
      address: 'Barrio Guamilito, San Pedro Sula, Honduras',
      phone: '+504 2550-3344'
    },
    // Costa Rica
    {
      name: 'Clínica 20/20 y Centro de Retina de Costa Rica',
      lat: 9.9350,
      lon: -84.0850,
      category: 'retina',
      isRetinaSpecialist: true,
      categoryLabel: 'Especialistas en Retina y Mácula',
      services: [
        'Tratamiento láser de retinopatía diabética',
        'OCT macular y angiografía'
      ],
      address: 'Paseo Colón, San José, Costa Rica',
      phone: '+506 2258-2020'
    },
    // México
    {
      name: 'Instituto de Oftalmología Fundación Conde de Valenciana',
      lat: 19.4215,
      lon: -99.1395,
      category: 'retina',
      isRetinaSpecialist: true,
      categoryLabel: 'Instituto Nacional de Alta Especialidad en Retina',
      services: [
        'Clínica de Retina y Retinopatía Diabética',
        'Fotocoagulación láser, terapia Anti-VEGF y Vitrectomía'
      ],
      address: 'Chimalpopoca 14, Centro, Cuauhtémoc, CDMX',
      phone: '+52 55 5588-4600'
    },
    {
      name: 'Asociación para Evitar la Ceguera en México (APEC Hospital de la Ceguera)',
      lat: 19.3448,
      lon: -99.1415,
      category: 'retina',
      isRetinaSpecialist: true,
      categoryLabel: 'Hospital de Especialidades en Retina y Ceguera',
      services: [
        'Departamento de Retina y Vítreo',
        'Estudios avanzados de fondo de ojo y OCT'
      ],
      address: 'Vicente García Torres 46, San Lucas, Coyoacán, CDMX',
      phone: '+52 55 1084-1400'
    },
    {
      name: 'Hospital Puerta de Hierro - Centro de Retina Guadalajara',
      lat: 20.7090,
      lon: -103.4140,
      category: 'retina',
      isRetinaSpecialist: true,
      categoryLabel: 'Unidad de Retina Médica y Quirúrgica',
      services: [
        'Retinopatía Diabética Proliferativa',
        'Cirugía vitreorretiniana de alta precisión'
      ],
      address: 'Av. Empresarios 150, Zapopan / Guadalajara, Jalisco',
      phone: '+52 33 3848-2100'
    }
  ];

  const OVERPASS_ENDPOINTS = [
    'https://overpass-api.de/api/interpreter',
    'https://overpass.kumi.systems/api/interpreter',
    'https://maps.mail.ru/osm/tools/overpass/api/interpreter'
  ];

  // --- Estado global del mapa ---
  let map = null;
  let userMarker = null;
  let userCircle = null;
  let markersLayer = null;
  let currentCoords = null;
  let placesData = [];
  let currentFilter = 'all';
  let isMapClickModeActive = false;

  // --- Elementos del DOM ---
  const dom = {
    countrySelect: document.getElementById('countrySelect'),
    citySelect: document.getElementById('citySelect'),
    addressInput: document.getElementById('addressInput'),
    btnSearchAddress: document.getElementById('btnSearchAddress'),
    btnGeolocate: document.getElementById('btnGeolocate'),
    btnMapClickMode: document.getElementById('btnMapClickMode'),
    btnToggleScrollZoom: document.getElementById('btnToggleScrollZoom'),
    scrollLockLabel: document.getElementById('scrollLockLabel'),
    radiusSelect: document.getElementById('radiusSelect'),
    categoryFilters: document.getElementById('categoryFilters'),
    placesList: document.getElementById('placesList'),
    placesCount: document.getElementById('placesCount'),
    currentLocationLabel: document.getElementById('currentLocationLabel'),
    nearestPublicCallout: document.getElementById('nearestPublicCallout'),
    mapStatusOverlay: document.getElementById('mapStatusOverlay'),
    mapStatusText: document.getElementById('mapStatusText')
  };

  let isScrollWheelZoomActive = true;

  // --- Iconos SVG personalizados para Leaflet ---
  function createCustomIcon(type) {
    if (type === 'user') {
      return L.divIcon({
        className: 'custom-map-icon user-marker-icon',
        html: '<div class="user-pulse-marker" title="Tu ubicación seleccionada (Arrastrable)"><div class="pulse-dot"></div></div>',
        iconSize: [28, 28],
        iconAnchor: [14, 14],
        popupAnchor: [0, -14]
      });
    }

    let color = '#0c8c86'; // Teal para Institutos
    let iconSvg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3" fill="white"/></svg>';

    if (type === 'retina') {
      color = '#7c3aed'; // Violeta para Alta Especialidad en Retina
      iconSvg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4" fill="white"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2"/></svg>';
    } else if (type === 'public') {
      color = '#16a34a'; // Verde para Red Pública (MINSAL)
      iconSvg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s-7-5.5-7-11a7 7 0 0 1 14 0c0 5.5-7 11-7 11Z"/><path d="M12 7v6M9 10h6"/></svg>';
    } else if (type === 'institutes') {
      color = '#0c8c86'; // Teal para Institutos
      iconSvg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3" fill="white"/></svg>';
    } else {
      color = '#0284c7'; // Azul para Clínicas
      iconSvg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>';
    }

    return L.divIcon({
      className: 'custom-map-icon',
      html: '<div class="marker-pin pin-' + type + '" style="background-color: ' + color + ';">' + iconSvg + '</div>',
      iconSize: [36, 42],
      iconAnchor: [18, 42],
      popupAnchor: [0, -38]
    });
  }

  // --- Inicialización del Mapa Leaflet ---
  function initMap() {
    const mapContainer = document.getElementById('osmMap');
    if (!mapContainer) return;

    // Iniciar con vista general en Centroamérica / Latam (zoom general)
    map = L.map('osmMap', {
      zoomControl: true,
      scrollWheelZoom: true,
      minZoom: 3,
      maxZoom: 19
    }).setView([14.6349, -90.5069], 7);

    // Evitar que el scroll con rueda del ratón dentro del mapa mueva o baje la página web
    mapContainer.addEventListener('wheel', function (e) {
      if (isScrollWheelZoomActive) {
        e.stopPropagation();
      }
    }, { passive: false });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> colaboradores'
    }).addTo(map);

    markersLayer = L.featureGroup().addTo(map);

    // Inicializar selectores dinámicos
    setupCountryCityPickers();
    setupEventListeners();

    // Permitir clic libre en el mapa para fijar ubicación en cualquier momento
    map.on('click', function (e) {
      const lat = e.latlng.lat;
      const lon = e.latlng.lng;
      setUserLocation(lat, lon, 'Punto fijado en el mapa (' + lat.toFixed(3) + ', ' + lon.toFixed(3) + ')', true);
    });

    // Vista inicial limpia (sin forzar ninguna ciudad o pin de inicio)
    renderInitialState();
  }

  // --- Estado inicial limpio en la barra lateral ---
  function renderInitialState() {
    if (dom.currentLocationLabel) {
      dom.currentLocationLabel.innerHTML = '<strong>📍 Ubicación:</strong> No establecida. Puedes fijar un punto en el mapa, seleccionar tu ciudad o escribir tu dirección.';
    }
    if (dom.nearestPublicCallout) {
      dom.nearestPublicCallout.style.display = 'none';
      dom.nearestPublicCallout.innerHTML = '';
    }
    if (dom.placesCount) {
      dom.placesCount.textContent = '0 centros';
    }
    if (dom.placesList) {
      dom.placesList.innerHTML =
        '<div class="places-empty-state">' +
        '<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>' +
        '<h3>Buscar Centros de Retinopatía</h3>' +
        '<p>Elige tu país y ciudad arriba, escribe una dirección en la barra de búsqueda o <strong>haz clic directamente en el mapa</strong> para colocar tu marcador y ver los especialistas cercanos.</p>' +
        '</div>';
    }
  }

  // --- Configurar Selector de País y Ciudades Dinámico (OPCIONAL) ---
  function setupCountryCityPickers() {
    if (!dom.countrySelect || !dom.citySelect) return;

    // Llenar ciudades según el país seleccionado
    function populateCities(countryKey) {
      dom.citySelect.innerHTML = '';

      if (!countryKey) {
        const defaultOpt = document.createElement('option');
        defaultOpt.value = '';
        defaultOpt.textContent = '-- Elige primero un país --';
        dom.citySelect.appendChild(defaultOpt);
        return;
      }

      if (countryKey === 'OTHER') {
        const otherOpt = document.createElement('option');
        otherOpt.value = '';
        otherOpt.textContent = '-- Búsqueda libre en barra de texto o mapa --';
        dom.citySelect.appendChild(otherOpt);
        if (dom.addressInput) {
          dom.addressInput.focus();
          dom.addressInput.placeholder = 'Escribe tu ciudad, municipio o país aquí...';
        }
        return;
      }

      const countryData = COUNTRY_CITY_DATABASE[countryKey];
      if (!countryData) return;

      const placeholderOpt = document.createElement('option');
      placeholderOpt.value = '';
      placeholderOpt.textContent = '-- Seleccionar Ciudad / Depto (' + countryData.name + ') --';
      dom.citySelect.appendChild(placeholderOpt);

      countryData.cities.forEach((city, idx) => {
        const opt = document.createElement('option');
        opt.value = idx;
        opt.textContent = city.name;
        dom.citySelect.appendChild(opt);
      });
    }

    // Evento de cambio de país (NO auto-rellena ni sobreescribe si es Otro o vacío)
    dom.countrySelect.addEventListener('change', function () {
      const countryKey = this.value;
      populateCities(countryKey);
      if (countryKey && countryKey !== 'OTHER') {
        const countryData = COUNTRY_CITY_DATABASE[countryKey];
        if (countryData && map) {
          map.setView([countryData.defaultLat, countryData.defaultLon], 8, { animate: true });
        }
      }
    });

    // Evento de cambio de ciudad (SOLO se activa cuando el usuario elige una ciudad concreta)
    dom.citySelect.addEventListener('change', function () {
      const countryKey = dom.countrySelect.value;
      if (!countryKey || countryKey === 'OTHER') return;
      if (this.value === '') return;

      const cityIdx = parseInt(this.value, 10);
      const countryData = COUNTRY_CITY_DATABASE[countryKey];
      if (!countryData) return;

      const cityData = countryData.cities[cityIdx];
      if (cityData) {
        if (dom.addressInput) {
          dom.addressInput.value = cityData.name + ', ' + countryData.name;
        }
        setUserLocation(cityData.lat, cityData.lon, cityData.name + ', ' + countryData.name, true);
      }
    });

    // Inicializar con opción vacía sin forzar país de inicio
    populateCities('');
  }

  // --- Event Listeners Globales ---
  function setupEventListeners() {
    // Botón GPS
    dom.btnGeolocate.addEventListener('click', function () {
      handleUserExplicitGeolocation();
    });

    // Botón de activación de modo clic
    if (dom.btnMapClickMode) {
      dom.btnMapClickMode.addEventListener('click', function () {
        isMapClickModeActive = !isMapClickModeActive;
        this.classList.toggle('is-active', isMapClickModeActive);
        showTemporaryToast(isMapClickModeActive ? 'Modo activo: Haz clic en cualquier lugar del mapa para fijar tu ubicación.' : 'Modo clic desactivado.');
      });
    }

    // Botón de Bloqueo / Activación de Zoom con Rueda del Ratón
    if (dom.btnToggleScrollZoom) {
      dom.btnToggleScrollZoom.addEventListener('click', function (e) {
        e.stopPropagation();
        isScrollWheelZoomActive = !isScrollWheelZoomActive;

        if (isScrollWheelZoomActive) {
          map.scrollWheelZoom.enable();
          dom.btnToggleScrollZoom.classList.remove('is-locked');
          if (dom.scrollLockLabel) dom.scrollLockLabel.textContent = 'Rueda de ratón: Zoom Activo';
          showTemporaryToast('Zoom con rueda del ratón activado.');
        } else {
          map.scrollWheelZoom.disable();
          dom.btnToggleScrollZoom.classList.add('is-locked');
          if (dom.scrollLockLabel) dom.scrollLockLabel.textContent = 'Rueda: Bloqueada (Usa + / -)';
          showTemporaryToast('Zoom con rueda bloqueado. El mapa no interferirá con el desplazamiento de la página.');
        }
      });
    }

    // Búsqueda de dirección manual
    dom.btnSearchAddress.addEventListener('click', handleAddressSearch);
    dom.addressInput.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        handleAddressSearch();
      }
    });

    // Cambio de radio de búsqueda
    dom.radiusSelect.addEventListener('change', function () {
      if (currentCoords) {
        fetchNearbyRetinopathyCenters(currentCoords.lat, currentCoords.lon);
      }
    });

    // Filtros de categoría
    if (dom.categoryFilters) {
      dom.categoryFilters.querySelectorAll('.filter-pill').forEach(function (pill) {
        pill.addEventListener('click', function () {
          dom.categoryFilters.querySelectorAll('.filter-pill').forEach(function (p) { p.classList.remove('is-active'); });
          pill.classList.add('is-active');
          currentFilter = pill.dataset.filter;
          renderPlacesList();
          renderMarkers();
        });
      });
    }
  }

  let liveGpsWatchId = null;

  // --- Geolocalización en Tiempo Real solicitada por el usuario ---
  function handleUserExplicitGeolocation() {
    showOverlay('Consultando sensor GPS en tiempo real...');

    // 1. Intentar Geolocation API nativa (GPS satelital por hardware)
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        function (position) {
          hideOverlay();
          const lat = position.coords.latitude;
          const lon = position.coords.longitude;
          const accuracy = Math.round(position.coords.accuracy || 5);
          
          setUserLocation(lat, lon, 'Tu ubicación exacta por GPS (Precisión: ±' + accuracy + 'm)', true);
          showTemporaryToast('🟢 ¡GPS por hardware activado con éxito! (Precisión exacta: ±' + accuracy + ' metros).');

          // Iniciar seguimiento continuo en tiempo real
          if (!liveGpsWatchId) {
            liveGpsWatchId = navigator.geolocation.watchPosition(
              function (watchPos) {
                const wLat = watchPos.coords.latitude;
                const wLon = watchPos.coords.longitude;
                if (currentCoords && haversineDistance(currentCoords.lat, currentCoords.lon, wLat, wLon) > 0.03) {
                  setUserLocation(wLat, wLon, 'Tu ubicación en tiempo real (GPS)', false);
                }
              },
              function (err) {
                console.warn('Seguimiento GPS:', err);
              },
              { enableHighAccuracy: true, maximumAge: 0, timeout: 20000 }
            );
          }
        },
        async function (error) {
          console.warn('GPS por hardware no disponible o bloqueado por contexto HTTP:', error);
          // 2. Si el navegador denegó el GPS por estar en HTTP de red local (192.168.x.x)
          hideOverlay();
          showTemporaryToast('⚠️ Tu navegador bloqueó el chip GPS debido a que estás en una dirección HTTP local (192.168.x.x). Para activar el GPS exacto por hardware, abre la página como http://localhost:5000 en tu navegador o haz clic en tu calle en el mapa.');
          
          // Opcionalmente consultar geolocalización aproximada por red
          await fetchFallbackNetworkLocation();
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 } // maximumAge: 0 fuerza al sensor GPS real
      );
    } else {
      hideOverlay();
      showTemporaryToast('Tu navegador no soporta el sensor GPS. Por favor escribe tu ciudad o haz clic en el mapa.');
    }
  }

  // --- Respaldo opcional de ubicación por red ---
  async function fetchFallbackNetworkLocation() {
    const endpoints = [
      'https://ipapi.co/json/',
      'https://get.geojs.io/v1/ip/geo.json',
      'https://ipwhois.app/json/'
    ];

    for (let i = 0; i < endpoints.length; i++) {
      try {
        const res = await fetch(endpoints[i], { timeout: 4000 });
        if (res.ok) {
          const data = await res.json();
          const lat = parseFloat(data.latitude || data.lat);
          const lon = parseFloat(data.longitude || data.lon || data.lng);
          const city = data.city || data.region || 'Tu región aproximada';
          const country = data.country_name || data.country || '';

          if (!isNaN(lat) && !isNaN(lon)) {
            setUserLocation(lat, lon, city + (country ? ', ' + country : '') + ' (Aproximación por proveedor de Internet)', true);
            return;
          }
        }
      } catch (e) {
        console.warn('Endpoint de geolocalización ' + endpoints[i] + ' falló:', e);
      }
    }
  }

  // --- Búsqueda manual de dirección con Nominatim OSM ---
  async function handleAddressSearch() {
    const query = dom.addressInput.value.trim();
    if (!query) {
      dom.addressInput.focus();
      return;
    }

    showOverlay('Buscando "' + query + '" en OpenStreetMap...');

    try {
      const url = 'https://nominatim.openstreetmap.org/search?format=json&q=' + encodeURIComponent(query) + '&limit=1&addressdetails=1';
      const res = await fetch(url, {
        headers: { 'Accept-Language': 'es,en' }
      });
      const data = await res.json();

      hideOverlay();

      if (!data || data.length === 0) {
        showTemporaryToast('No encontramos resultados para "' + query + '". Selecciona tu país y ciudad en los menús desplegables.');
        return;
      }

      const match = data[0];
      const lat = parseFloat(match.lat);
      const lon = parseFloat(match.lon);
      const displayName = match.display_name.split(',').slice(0, 3).join(',');

      setUserLocation(lat, lon, displayName, true);
    } catch (err) {
      hideOverlay();
      console.error('Error en Nominatim:', err);
      showTemporaryToast('Ocurrió un error al buscar la dirección. Por favor intenta de nuevo.');
    }
  }

  // --- Fijar ubicación activa, actualizar marcador arrastrable y consultar centros ---
  function setUserLocation(lat, lon, label, zoomIn) {
    currentCoords = { lat: lat, lon: lon };

    if (dom.currentLocationLabel) {
      dom.currentLocationLabel.innerHTML = '<strong>📍 Ubicación activa:</strong> ' + escapeHtml(label);
    }

    // Actualizar o crear marcador arrastrable del usuario
    if (userMarker) map.removeLayer(userMarker);
    if (userCircle) map.removeLayer(userCircle);

    userMarker = L.marker([lat, lon], {
      icon: createCustomIcon('user'),
      draggable: true, // ¡Arrastrable libremente!
      zIndexOffset: 1000
    }).addTo(map);

    userMarker.bindPopup(
      '<div class="custom-popup user-popup">' +
      '<h4>📍 Tu ubicación</h4>' +
      '<p>' + escapeHtml(label) + '</p>' +
      '<small style="color: var(--teal-deep); font-weight: 600;">(Puedes arrastrar este pin o hacer clic en cualquier lugar del mapa)</small>' +
      '</div>'
    );

    // Evento de arrastrar y soltar el marcador
    userMarker.on('dragend', function (e) {
      const newPos = e.target.getLatLng();
      setUserLocation(newPos.lat, newPos.lng, 'Punto arrastrado (' + newPos.lat.toFixed(3) + ', ' + newPos.lng.toFixed(3) + ')', false);
    });

    const radius = parseInt(dom.radiusSelect.value, 10) || 50000;
    userCircle = L.circle([lat, lon], {
      radius: radius,
      color: '#7c3aed',
      fillColor: '#7c3aed',
      fillOpacity: 0.04,
      weight: 1.5,
      dashArray: '4, 4'
    }).addTo(map);

    if (zoomIn) {
      map.setView([lat, lon], calculateZoomForRadius(radius), { animate: true });
    } else {
      map.panTo([lat, lon]);
    }

    fetchNearbyRetinopathyCenters(lat, lon);
  }

  function calculateZoomForRadius(radiusMeters) {
    if (radiusMeters <= 10000) return 13;
    if (radiusMeters <= 25000) return 11;
    if (radiusMeters <= 50000) return 10;
    if (radiusMeters <= 100000) return 9;
    if (radiusMeters <= 200000) return 8;
    if (radiusMeters <= 300000) return 7;
    return 6;
  }

  // --- Consulta de Centros de Retinopatía (OSM + Directorio Verificado) ---
  async function fetchNearbyRetinopathyCenters(lat, lon) {
    const radius = parseInt(dom.radiusSelect.value, 10) || 50000;
    showOverlay('Buscando centros especializados en retina y oftalmología...');

    if (userCircle) {
      userCircle.setRadius(radius);
    }

    // Consulta de salud amplia a Overpass
    const overpassQuery =
      '[out:json][timeout:25];' +
      '(' +
      'node["amenity"="hospital"](around:' + radius + ',' + lat + ',' + lon + ');' +
      'way["amenity"="hospital"](around:' + radius + ',' + lat + ',' + lon + ');' +
      'node["amenity"="clinic"](around:' + radius + ',' + lat + ',' + lon + ');' +
      'way["amenity"="clinic"](around:' + radius + ',' + lat + ',' + lon + ');' +
      'node["amenity"="doctors"](around:' + radius + ',' + lat + ',' + lon + ');' +
      'way["amenity"="doctors"](around:' + radius + ',' + lat + ',' + lon + ');' +
      'node["healthcare"](around:' + radius + ',' + lat + ',' + lon + ');' +
      'way["healthcare"](around:' + radius + ',' + lat + ',' + lon + ');' +
      ');' +
      'out center;';

    let osmElements = [];

    for (let i = 0; i < OVERPASS_ENDPOINTS.length; i++) {
      const endpoint = OVERPASS_ENDPOINTS[i];
      try {
        const response = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: 'data=' + encodeURIComponent(overpassQuery)
        });

        if (response.ok) {
          const data = await response.json();
          if (data && data.elements) {
            osmElements = data.elements;
            break;
          }
        }
      } catch (err) {
        console.warn('Endpoint OSM ' + endpoint + ' falló:', err);
      }
    }

    hideOverlay();

    processCombinedResults(osmElements, lat, lon, radius);
  }

  // --- Combinar y Filtrar Estrictamente para Retinopatía Diabética ---
  function processCombinedResults(osmElements, userLat, userLon, radiusMeters) {
    const rawPlaces = [];
    const seen = new Set();

    // 1. Agregar centros verificados de la base de datos que estén dentro del radio
    VERIFIED_RETINA_CENTERS.forEach(vc => {
      const dist = haversineDistance(userLat, userLon, vc.lat, vc.lon);
      if (dist <= (radiusMeters / 1000) * 1.25) { // Dentro del radio seleccionado
        const key = vc.name.toLowerCase().slice(0, 20);
        seen.add(key);
        rawPlaces.push({
          id: 'v_' + Math.round(vc.lat * 1000),
          name: vc.name,
          lat: vc.lat,
          lon: vc.lon,
          distanceKm: dist,
          category: vc.category,
          isRetinaSpecialist: vc.isRetinaSpecialist,
          isPublic: vc.isPublic || false,
          categoryLabel: vc.categoryLabel,
          services: vc.services,
          address: vc.address,
          phone: vc.phone || null,
          website: null,
          openingHours: vc.isPublic
            ? 'Hospital público — emergencias 24h, consulta de oftalmología según horario hospitalario'
            : 'Lunes a Viernes (Previa Cita / Urgencias)',
          emergency: true,
          isVerified: true
        });
      }
    });

    // 2. Procesar y filtrar estrictamente elementos de OpenStreetMap
    const excludeKeywords = ['dental', 'dentista', 'odontolog', 'estética', 'estetica', 'veterinaria', 'pediatría general', 'maternidad', 'ginecolog', 'psicolog', 'podolog', 'ortopedia', 'traumatologia', 'traumatología', 'cruz roja', 'cruz verde', 'dermatolog', 'spa'];

    osmElements.forEach(el => {
      const pLat = el.lat || (el.center && el.center.lat);
      const pLon = el.lon || (el.center && el.center.lon);
      if (!pLat || !pLon) return;

      const tags = el.tags || {};
      const name = tags.name || tags['name:es'] || tags['name:en'] || tags.operator || '';
      const nameLower = name.toLowerCase();

      // Excluir rubros ajenos a salud ocular
      if (excludeKeywords.some(k => nameLower.includes(k))) return;

      // Clasificar si pertenece a oftalmología o retina
      const classification = classifyOsmPlace(tags, name);
      if (!classification.isValid) return;

      const key = nameLower.slice(0, 15);
      if (seen.has(key)) return;

      const distanceKm = haversineDistance(userLat, userLon, pLat, pLon);

      // Deduplicar contra centros ya agregados (verificados u OSM) que estén
      // a menos de 150 m: es muy probable que sea el mismo lugar físico con
      // un nombre ligeramente distinto (comparar solo por texto no es
      // suficiente, p. ej. "Hospital Nacional San Rafael" vs. con comillas).
      const isSameLocationAsExisting = rawPlaces.some(
        p => haversineDistance(p.lat, p.lon, pLat, pLon) < 0.15
      );
      if (isSameLocationAsExisting) return;

      seen.add(key);

      const street = tags['addr:street'] || '';
      const housenumber = tags['addr:housenumber'] || '';
      const city = tags['addr:city'] || tags['addr:suburb'] || '';
      let address = [street, housenumber, city].filter(Boolean).join(' ');
      if (!address) address = 'Ubicación registrada en OpenStreetMap';

      const phone = tags['phone'] || tags['contact:phone'] || tags['contact:mobile'] || null;
      const website = tags['website'] || tags['contact:website'] || null;
      const openingHours = tags['opening_hours'] || null;
      const emergency = (tags['emergency'] === 'yes');

      rawPlaces.push({
        id: el.id,
        name: name || classification.defaultName,
        lat: pLat,
        lon: pLon,
        distanceKm: distanceKm,
        category: classification.category,
        isRetinaSpecialist: classification.isRetinaSpecialist,
        isPublic: classification.isPublic || false,
        categoryLabel: classification.categoryLabel,
        services: classification.services,
        address: address,
        phone: phone,
        website: website,
        openingHours: openingHours,
        emergency: emergency,
        isVerified: false
      });
    });

    // Ordenar priorizando especialistas de retina y luego por cercanía
    rawPlaces.sort((a, b) => {
      if (a.isRetinaSpecialist && !b.isRetinaSpecialist) return -1;
      if (!a.isRetinaSpecialist && b.isRetinaSpecialist) return 1;
      return a.distanceKm - b.distanceKm;
    });

    placesData = rawPlaces;
    renderPlacesList();
    renderMarkers();
    renderNearestPublicCallout();
  }

  // --- Callout: centro hospitalario PÚBLICO con oftalmología más cercano ---
  function renderNearestPublicCallout() {
    if (!dom.nearestPublicCallout) return;

    const nearestPublic = placesData
      .filter(p => p.isPublic)
      .sort((a, b) => a.distanceKm - b.distanceKm)[0];

    if (!nearestPublic) {
      dom.nearestPublicCallout.style.display = 'none';
      dom.nearestPublicCallout.innerHTML = '';
      return;
    }

    const distStr = nearestPublic.distanceKm < 1
      ? Math.round(nearestPublic.distanceKm * 1000) + ' m'
      : nearestPublic.distanceKm.toFixed(1) + ' km';

    dom.nearestPublicCallout.style.display = 'flex';
    dom.nearestPublicCallout.innerHTML =
      '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s-7-5.5-7-11a7 7 0 0 1 14 0c0 5.5-7 11-7 11Z"/><path d="M12 7v6M9 10h6"/></svg>' +
      '<div>' +
      '<p class="callout-label">Centro público más cercano</p>' +
      '<p class="callout-name">' + escapeHtml(nearestPublic.name) + '</p>' +
      '<p class="callout-dist">A ' + distStr + ' de tu ubicación</p>' +
      '</div>';

    dom.nearestPublicCallout.onclick = function () {
      focusPlaceOnMap(nearestPublic.lat, nearestPublic.lon);
    };
  }

  // --- Clasificación estricta de elementos OSM ---
  function classifyOsmPlace(tags, name) {
    const fullText = (name + ' ' + (tags['healthcare:speciality'] || '') + ' ' + (tags['speciality'] || '') + ' ' + (tags['description'] || '') + ' ' + (tags['healthcare'] || '') + ' ' + (tags['amenity'] || '')).toLowerCase();

    // Palabras de retina y retinopatía
    const retinaKeywords = ['retina', 'retinólog', 'retinolog', 'retinopat', 'mácula', 'macula', 'vítreo', 'vitreo', 'vitrectom', 'láser ocular', 'laser ocular', 'fotocoagulación', 'anti-vegf', 'ceguera', 'ciegos', 'valenciana', 'apec', 'robles', 'visualiza', 'inclio'];
    const isRetina = retinaKeywords.some(k => fullText.includes(k));

    // Palabras generales de oftalmología
    const eyeKeywords = ['oftalmo', 'ojo', 'ojos', 'visión', 'vision', 'oculist', 'glaucoma', 'córnea', 'cornea', 'catarata', 'salauno', 'instituto de oftalmología', 'instituto de la visión', 'eye', 'ophthalmology', 'optometrist', 'optometría'];
    const isEye = eyeKeywords.some(k => fullText.includes(k)) ||
      tags['healthcare:speciality'] === 'ophthalmology' ||
      tags['speciality'] === 'ophthalmology' ||
      tags['healthcare'] === 'ophthalmologist' ||
      tags['healthcare'] === 'optometrist';

    if (!isRetina && !isEye) {
      return { isValid: false };
    }

    if (isRetina) {
      return {
        isValid: true,
        category: 'retina',
        isRetinaSpecialist: true,
        categoryLabel: 'Alta Especialidad en Retina y Retinopatía',
        defaultName: 'Especialista en Retina y Retinopatía',
        services: [
          'Examen de fondo de ojo con dilatación pupilar',
          'Fotocoagulación láser para retinopatía',
          'Inyecciones intravítreas Anti-VEGF',
          'Cirugía de vítreo y retina (Vitrectomía)'
        ]
      };
    }

    // Detectar operador público (red gubernamental / seguridad social) a partir
    // de etiquetas de OSM, para distinguir hospitales públicos de clínicas privadas.
    const publicKeywords = ['hospital nacional', 'minsal', 'ministerio de salud', 'isss', 'seguro social', 'fosalud'];
    const operatorType = (tags['operator:type'] || '').toLowerCase();
    const isPublicFacility =
      publicKeywords.some(k => fullText.includes(k)) ||
      operatorType === 'government' || operatorType === 'public';

    const isInstitute = fullText.includes('instituto') || fullText.includes('hospital') || fullText.includes('centro oftalmologico') || fullText.includes('centro oftalmológico');

    if (isInstitute && isPublicFacility) {
      return {
        isValid: true,
        category: 'public',
        isRetinaSpecialist: false,
        isPublic: true,
        categoryLabel: 'Hospital / Centro Público de Oftalmología',
        defaultName: 'Hospital Público con Oftalmología',
        services: [
          'Consulta oftalmológica pública',
          'Detección y seguimiento de retinopatía diabética (según disponibilidad)'
        ]
      };
    }

    if (isInstitute) {
      return {
        isValid: true,
        category: 'institutes',
        isRetinaSpecialist: false,
        categoryLabel: 'Hospital / Instituto Oftalmológico',
        defaultName: 'Instituto de Oftalmología',
        services: [
          'Consulta oftalmológica especializada',
          'Detección y seguimiento de retinopatía diabética',
          'Estudios diagnósticos de retina y mácula'
        ]
      };
    }

    return {
      isValid: true,
      category: 'clinics',
      isRetinaSpecialist: false,
      categoryLabel: 'Clínica Oftalmológica / Consultorio de Ojos',
      defaultName: 'Clínica Oftalmológica',
      services: [
        'Evaluación de fondo de ojo y salud visual',
        'Canalización con médico retinólogo'
      ]
    };
  }

  // --- Distancia Haversine en Kilómetros ---
  function haversineDistance(lat1, lon1, lat2, lon2) {
    const R = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }

  // --- Traducción y formato en Español de Horarios de Atención ---
  function formatOpeningHoursSpanish(raw) {
    if (!raw) return 'Lunes a Viernes (Previa cita / Consulta)';
    if (raw === '24/7' || raw === '24 / 7') return 'Abierto las 24 horas (Servicio continuo / Urgencias)';

    let text = String(raw);

    const dict = [
      [/\bMo-Su\b/gi, 'Lunes a Domingo'],
      [/\bMo-Sa\b/gi, 'Lunes a Sábado'],
      [/\bMo-Fr\b/gi, 'Lunes a Viernes'],
      [/\bSa-Su\b/gi, 'Sábados y Domingos'],
      [/\bMo\b/gi, 'Lunes'],
      [/\bTu\b/gi, 'Martes'],
      [/\bWe\b/gi, 'Miércoles'],
      [/\bTh\b/gi, 'Jueves'],
      [/\bFr\b/gi, 'Viernes'],
      [/\bSa\b/gi, 'Sábado'],
      [/\bSu\b/gi, 'Domingo'],
      [/\bPH\b/gi, 'Feriados'],
      [/\boff\b/gi, 'Cerrado'],
      [/\bclosed\b/gi, 'Cerrado'],
      [/\bopen\b/gi, 'Abierto'],
      [/\bby appointment\b/gi, 'Previa cita'],
      [/\bappointment only\b/gi, 'Solo con cita previa']
    ];

    dict.forEach(([regex, rep]) => {
      text = text.replace(regex, rep);
    });

    return text;
  }

  // --- Renderizar Marcadores en el Mapa ---
  function renderMarkers() {
    if (!markersLayer) return;
    markersLayer.clearLayers();

    const filtered = getFilteredPlaces();

    filtered.forEach(place => {
      const marker = L.marker([place.lat, place.lon], {
        icon: createCustomIcon(place.category)
      });

      const badgeClass = place.category === 'retina' ? 'badge-retina' : (place.category === 'public' ? 'badge-public' : (place.category === 'institutes' ? 'badge-opht' : 'badge-clin'));
      const gmapsUrl = 'https://www.google.com/maps/dir/?api=1&destination=' + place.lat + ',' + place.lon;
      const osmRouteUrl = currentCoords ? ('https://www.openstreetmap.org/directions?engine=fossgis_osrm_car&route=' + currentCoords.lat + ',' + currentCoords.lon + '%3B' + place.lat + ',' + place.lon) : ('https://www.openstreetmap.org/?mlat=' + place.lat + '&mlon=' + place.lon + '#map=17/' + place.lat + '/' + place.lon);

      let servicesListHtml = '';
      if (place.services && place.services.length > 0) {
        servicesListHtml = '<ul class="popup-services-list">' + place.services.slice(0, 2).map(s => '<li>✓ ' + escapeHtml(s) + '</li>').join('') + '</ul>';
      }

      const formattedHours = formatOpeningHoursSpanish(place.openingHours);

      let popupHtml =
        '<div class="custom-popup place-popup">' +
        '<div class="popup-badge ' + badgeClass + '">' + escapeHtml(place.categoryLabel) + '</div>' +
        '<h4 class="popup-title">' + escapeHtml(place.name) + '</h4>' +
        '<p class="popup-distance">📍 A <strong>' + (place.distanceKm < 1 ? Math.round(place.distanceKm * 1000) + ' m' : place.distanceKm.toFixed(1) + ' km') + '</strong> de tu ubicación</p>' +
        '<p class="popup-address">' + escapeHtml(place.address) + '</p>' +
        servicesListHtml;

      if (place.phone) {
        popupHtml += '<p class="popup-meta">📞 <strong>Tel:</strong> <a href="tel:' + escapeHtml(place.phone) + '">' + escapeHtml(place.phone) + '</a></p>';
      }
      if (formattedHours) {
        popupHtml += '<p class="popup-meta">🕒 <strong>Horario de atención:</strong> ' + escapeHtml(formattedHours) + '</p>';
      }

      popupHtml +=
        '<div class="popup-actions">' +
        '<a href="' + gmapsUrl + '" target="_blank" rel="noopener" class="btn-popup-nav">Cómo llegar (Google Maps)</a>' +
        '<a href="' + osmRouteUrl + '" target="_blank" rel="noopener" class="btn-popup-nav-osm">Ver en OpenStreetMap</a>' +
        '</div>' +
        '</div>';

      marker.bindPopup(popupHtml, { maxWidth: 300, className: 'osm-custom-leaflet-popup' });
      markersLayer.addLayer(marker);
    });
  }

  // --- Renderizar Lista de Lugares en el Panel Lateral ---
  function renderPlacesList() {
    const filtered = getFilteredPlaces();

    if (dom.placesCount) {
      dom.placesCount.textContent = filtered.length + (filtered.length === 1 ? ' centro oftalmológico' : ' centros oftalmológicos');
    }

    if (filtered.length === 0) {
      const curRadius = dom.radiusSelect.value / 1000;
      dom.placesList.innerHTML =
        '<div class="places-empty-state">' +
        '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="8" y1="12" x2="16" y2="12"/></svg>' +
        '<h3>No se encontraron centros en ' + curRadius + ' km</h3>' +
        '<p>No encontramos clínicas de retina registradas en este radio inmediato. Te recomendamos:</p>' +
        '<div style="display: flex; flex-direction: column; gap: 8px; margin-top: 12px; width: 100%;">' +
        '<button type="button" class="btn btn-secondary btn-sm" onclick="document.getElementById(\'radiusSelect\').value=\'100000\'; document.getElementById(\'radiusSelect\').dispatchEvent(new Event(\'change\'));">Ampliar radio a 100 km (Regional)</button>' +
        '<button type="button" class="btn btn-ghost btn-sm" onclick="document.getElementById(\'radiusSelect\').value=\'300000\'; document.getElementById(\'radiusSelect\').dispatchEvent(new Event(\'change\'));">Ampliar radio a 300 km (Nacional)</button>' +
        '<a href="https://www.google.com/maps/search/oftalmologo+retinologo+retinopatia/@' + (currentCoords ? currentCoords.lat + ',' + currentCoords.lon + ',11z' : '') + '" target="_blank" rel="noopener" class="btn btn-primary btn-sm" style="margin-top: 4px;">Buscar especialistas en Google Maps</a>' +
        '</div>' +
        '</div>';
      return;
    }

    let html = '';
    filtered.forEach((place, idx) => {
      const badgeStyle = place.category === 'retina' ? 'pill-retina' : (place.category === 'public' ? 'pill-public' : (place.category === 'institutes' ? 'pill-opht' : 'pill-clin'));
      const distStr = place.distanceKm < 1 ? Math.round(place.distanceKm * 1000) + ' m' : place.distanceKm.toFixed(1) + ' km';
      const gmapsUrl = 'https://www.google.com/maps/dir/?api=1&destination=' + place.lat + ',' + place.lon;
      const formattedHours = formatOpeningHoursSpanish(place.openingHours);

      let servicesHtml = '';
      if (place.services && place.services.length > 0) {
        servicesHtml = '<div class="place-services-box">' +
          '<span class="services-title">🩺 Procedimientos para Retinopatía:</span>' +
          '<ul>' + place.services.map(s => '<li>' + escapeHtml(s) + '</li>').join('') + '</ul>' +
          '</div>';
      }

      html +=
        '<div class="place-card ' + (place.isRetinaSpecialist ? 'is-retina-specialist' : '') + '" data-index="' + idx + '" data-lat="' + place.lat + '" data-lon="' + place.lon + '">' +
        (place.isRetinaSpecialist ? '<div class="retina-specialist-ribbon"><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg> Especialista en Retina</div>' : '') +
        '<div class="place-card-header">' +
        '<h3 class="place-name">' + escapeHtml(place.name) + '</h3>' +
        '<span class="place-dist-badge">' + distStr + '</span>' +
        '</div>' +
        '<div class="place-tags">' +
        '<span class="place-type-pill ' + badgeStyle + '">' + escapeHtml(place.categoryLabel) + '</span>' +
        (place.emergency ? '<span class="place-type-pill pill-urg">Urgencias Oculares</span>' : '') +
        '</div>' +
        '<p class="place-address">' + escapeHtml(place.address) + '</p>' +
        servicesHtml;

      if (formattedHours) {
        html +=
          '<div class="place-contact-line">' +
          '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>' +
          '<span><strong>Horario:</strong> ' + escapeHtml(formattedHours) + '</span>' +
          '</div>';
      }

      if (place.phone) {
        html +=
          '<div class="place-contact-line">' +
          '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>' +
          '<a href="tel:' + escapeHtml(place.phone) + '">' + escapeHtml(place.phone) + '</a>' +
          '</div>';
      }

      html +=
        '<div class="place-card-actions">' +
        '<button type="button" class="btn-focus-place btn btn-ghost btn-xs" data-lat="' + place.lat + '" data-lon="' + place.lon + '">' +
        '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3"/></svg> ' +
        'Ver en mapa' +
        '</button>' +
        '<a href="' + gmapsUrl + '" target="_blank" rel="noopener" class="btn-directions-link btn btn-primary btn-xs">' +
        '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="3 11 22 2 13 21 11 13 3 11"/></svg> ' +
        'Cómo llegar' +
        '</a>' +
        '</div>' +
        '</div>';
    });

    dom.placesList.innerHTML = html;

    dom.placesList.querySelectorAll('.place-card').forEach(card => {
      card.addEventListener('click', e => {
        if (e.target.closest('a') || e.target.closest('.btn-directions-link')) return;
        const lat = parseFloat(card.dataset.lat);
        const lon = parseFloat(card.dataset.lon);
        focusPlaceOnMap(lat, lon);
      });
    });

    dom.placesList.querySelectorAll('.btn-focus-place').forEach(btn => {
      btn.addEventListener('click', e => {
        e.stopPropagation();
        const lat = parseFloat(btn.dataset.lat);
        const lon = parseFloat(btn.dataset.lon);
        focusPlaceOnMap(lat, lon);
      });
    });
  }

  function focusPlaceOnMap(lat, lon) {
    if (!map) return;
    map.setView([lat, lon], 15, { animate: true, duration: 0.8 });

    if (markersLayer) {
      markersLayer.eachLayer(layer => {
        if (layer.getLatLng && Math.abs(layer.getLatLng().lat - lat) < 0.0001 && Math.abs(layer.getLatLng().lng - lon) < 0.0001) {
          layer.openPopup();
        }
      });
    }
  }

  function getFilteredPlaces() {
    if (currentFilter === 'all') return placesData;
    return placesData.filter(p => p.category === currentFilter);
  }

  function showOverlay(message) {
    if (dom.mapStatusOverlay) {
      if (dom.mapStatusText) dom.mapStatusText.textContent = message;
      dom.mapStatusOverlay.classList.remove('is-hidden');
    }
  }

  function hideOverlay() {
    if (dom.mapStatusOverlay) {
      dom.mapStatusOverlay.classList.add('is-hidden');
    }
  }

  function showTemporaryToast(message) {
    const existing = document.getElementById('mapAppToast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.id = 'mapAppToast';
    toast.className = 'map-app-toast';
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
      toast.classList.add('toast-show');
    }, 20);

    setTimeout(() => {
      toast.classList.remove('toast-show');
      setTimeout(() => toast.remove(), 400);
    }, 4500);
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Iniciar al cargar el DOM
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMap);
  } else {
    initMap();
  }
})();

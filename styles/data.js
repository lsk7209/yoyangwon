/* Sample data — FICTIONAL facilities for demonstration only.
   Mirrors the shape of CMS Care Compare / Provider Info datasets. */
window.FACILITIES = [
  {
    id: 'maplewood', name: 'Maplewood Health & Rehabilitation',
    city: 'Springfield, IL', address: '1820 W Monroe St, Springfield, IL 62704',
    ownership: 'For-profit', beds: 142, occupancy: 88,
    overall: 2, health: 2, staffing: 3, qm: 3,
    pctile: 34, trend: [4,4,3,3,2,2], trendNote: '4★ → 2★ over 18 mo',
    rnHrs: 0.52, totalHrs: 3.41, turnover: 58,
    deficiencies: 14, sevHigh: 2, fines: 21400, sff: false, abuse: true,
    distance: 2.1
  },
  {
    id: 'riverside', name: 'Riverside Care Center',
    city: 'Springfield, IL', address: '405 N Grand Ave E, Springfield, IL 62702',
    ownership: 'Non-profit', beds: 96, occupancy: 91,
    overall: 4, health: 4, staffing: 4, qm: 4,
    pctile: 78, trend: [3,3,4,4,4,4], trendNote: 'Stable at 4★, 24 mo',
    rnHrs: 0.91, totalHrs: 4.12, turnover: 33,
    deficiencies: 4, sevHigh: 0, fines: 0, sff: false, abuse: false,
    distance: 3.4
  },
  {
    id: 'oakhaven', name: 'Oakhaven Skilled Nursing',
    city: 'Springfield, IL', address: '2700 Lawrence Ave, Springfield, IL 62703',
    ownership: 'For-profit', beds: 188, occupancy: 79,
    overall: 1, health: 1, staffing: 2, qm: 2,
    pctile: 8, trend: [2,2,1,1,1,1], trendNote: 'On SFF watch list',
    rnHrs: 0.38, totalHrs: 3.02, turnover: 71,
    deficiencies: 22, sevHigh: 4, fines: 86250, sff: true, abuse: true,
    distance: 4.0
  },
  {
    id: 'cedarridge', name: 'Cedar Ridge Nursing & Rehab',
    city: 'Decatur, IL', address: '560 W Ash Ave, Decatur, IL 62526',
    ownership: 'For-profit', beds: 120, occupancy: 84,
    overall: 3, health: 3, staffing: 3, qm: 4,
    pctile: 52, trend: [3,3,3,3,3,3], trendNote: 'Stable at 3★',
    rnHrs: 0.61, totalHrs: 3.68, turnover: 47,
    deficiencies: 8, sevHigh: 1, fines: 9800, sff: false, abuse: false,
    distance: 38.6
  },
  {
    id: 'prairievista', name: 'Prairie Vista Senior Care',
    city: 'Springfield, IL', address: '3300 Robbins Rd, Springfield, IL 62704',
    ownership: 'Non-profit', beds: 74, occupancy: 94,
    overall: 5, health: 5, staffing: 5, qm: 4,
    pctile: 92, trend: [4,4,5,5,5,5], trendNote: '4★ → 5★ over 18 mo',
    rnHrs: 1.14, totalHrs: 4.55, turnover: 24,
    deficiencies: 2, sevHigh: 0, fines: 0, sff: false, abuse: false,
    distance: 5.2
  },
  {
    id: 'lincolnpark', name: 'Lincoln Park Health Center',
    city: 'Springfield, IL', address: '950 N 5th St, Springfield, IL 62702',
    ownership: 'Government', beds: 110, occupancy: 86,
    overall: 3, health: 2, staffing: 4, qm: 3,
    pctile: 45, trend: [3,3,2,2,3,3], trendNote: 'Recovered to 3★',
    rnHrs: 0.74, totalHrs: 3.88, turnover: 41,
    deficiencies: 9, sevHigh: 1, fines: 4200, sff: false, abuse: false,
    distance: 1.6
  }
];

/* Deficiency timeline sample (Maplewood) — neutral, factual records */
window.DEFICIENCIES = [
  { date: '2025-11-14', ftag: 'F-689', scope: 'Pattern', sev: 'high', harm: 'Actual harm',
    text: 'Failed to ensure residents free from accident hazards; one resident sustained a fall-related fracture.', survey: 'Health inspection' },
  { date: '2025-11-14', ftag: 'F-684', scope: 'Isolated', sev: 'mid', harm: 'Actual harm',
    text: 'Quality of care: failed to provide treatment consistent with professional standards for two residents.', survey: 'Health inspection' },
  { date: '2025-06-02', ftag: 'F-812', scope: 'Widespread', sev: 'low', harm: 'Potential for harm',
    text: 'Food procurement and sanitary storage deficiencies identified in main kitchen.', survey: 'Health inspection' },
  { date: '2025-06-02', ftag: 'F-880', scope: 'Pattern', sev: 'mid', harm: 'Actual harm',
    text: 'Infection prevention and control program not fully implemented per facility policy.', survey: 'Health inspection' },
  { date: '2024-12-09', ftag: 'F-600', scope: 'Isolated', sev: 'high', harm: 'Immediate jeopardy',
    text: 'Failed to protect a resident from abuse; allegation substantiated following investigation.', survey: 'Complaint investigation' },
  { date: '2024-12-09', ftag: 'F-609', scope: 'Isolated', sev: 'mid', harm: 'Actual harm',
    text: 'Failed to report and investigate an allegation of abuse within required timeframe.', survey: 'Complaint investigation' },
  { date: '2024-03-21', ftag: 'F-758', scope: 'Pattern', sev: 'low', harm: 'Potential for harm',
    text: 'Free from unnecessary psychotropic medication: review documentation incomplete for three residents.', survey: 'Health inspection' }
];

/* Per-facility deficiency records, keyed by facility id. Neutral, factual. */
window.DEFS = {
  maplewood: window.DEFICIENCIES,
  riverside: [
    { date: '2025-09-08', ftag: 'F-636', scope: 'Isolated', sev: 'low', harm: 'Potential for harm',
      text: 'Comprehensive assessment not completed within required timeframe for one newly admitted resident.', survey: 'Health inspection' },
    { date: '2024-08-19', ftag: 'F-812', scope: 'Isolated', sev: 'low', harm: 'Potential for harm',
      text: 'Minor food-storage labeling deficiency identified and corrected on site during the standard survey.', survey: 'Health inspection' }
  ],
  oakhaven: [
    { date: '2026-02-18', ftag: 'F-600', scope: 'Isolated', sev: 'high', harm: 'Immediate jeopardy',
      text: 'Failed to protect residents from abuse; allegation substantiated. Immediate jeopardy abated after a plan of correction was accepted.', survey: 'Complaint investigation' },
    { date: '2025-09-30', ftag: 'F-690', scope: 'Pattern', sev: 'mid', harm: 'Actual harm',
      text: 'Bowel/bladder incontinence care not provided consistent with assessed needs for several residents.', survey: 'Health inspection' },
    { date: '2025-09-30', ftag: 'F-725', scope: 'Widespread', sev: 'mid', harm: 'Actual harm',
      text: 'Sufficient nursing staff not provided to meet residents’ assessed needs across multiple units.', survey: 'Health inspection' },
    { date: '2025-04-11', ftag: 'F-689', scope: 'Pattern', sev: 'high', harm: 'Immediate jeopardy',
      text: 'Failed to ensure residents free from accident hazards; an elopement occurred from an unsecured exit.', survey: 'Complaint investigation' },
    { date: '2024-10-22', ftag: 'F-686', scope: 'Pattern', sev: 'mid', harm: 'Actual harm',
      text: 'Pressure-injury prevention and treatment not consistent with professional standards for two residents.', survey: 'Health inspection' }
  ],
  cedarridge: [
    { date: '2025-07-05', ftag: 'F-812', scope: 'Pattern', sev: 'low', harm: 'Potential for harm',
      text: 'Food procurement and sanitary storage deficiencies identified in the main kitchen.', survey: 'Health inspection' },
    { date: '2025-07-05', ftag: 'F-684', scope: 'Isolated', sev: 'mid', harm: 'Actual harm',
      text: 'Quality of care: care plan not followed for one resident, resulting in a delayed treatment.', survey: 'Health inspection' },
    { date: '2024-06-14', ftag: 'F-758', scope: 'Isolated', sev: 'low', harm: 'Potential for harm',
      text: 'Psychotropic medication review documentation incomplete for two residents.', survey: 'Health inspection' }
  ],
  prairievista: [
    { date: '2025-05-20', ftag: 'F-761', scope: 'Isolated', sev: 'info', harm: 'No actual harm',
      text: 'Medication labeling and storage finding with no actual harm; corrected during the survey.', survey: 'Health inspection' }
  ],
  lincolnpark: [
    { date: '2025-08-12', ftag: 'F-880', scope: 'Widespread', sev: 'mid', harm: 'Actual harm',
      text: 'Infection prevention and control program not fully implemented per facility policy.', survey: 'Health inspection' },
    { date: '2024-11-03', ftag: 'F-657', scope: 'Pattern', sev: 'low', harm: 'Potential for harm',
      text: 'Care plans not reviewed and revised by the interdisciplinary team within required intervals.', survey: 'Health inspection' },
    { date: '2024-11-03', ftag: 'F-550', scope: 'Isolated', sev: 'low', harm: 'Potential for harm',
      text: 'Resident dignity finding regarding shared-room privacy; addressed in plan of correction.', survey: 'Health inspection' }
  ]
};

/**
 * TARU survey builder (Google Apps Script)
 * ---------------------------------------------------------------
 * Builds the full TARU survey from Appendix A5 of the project brief:
 * consent, screener, purchase history, 3-arm claim test (arm assigned by
 * day of birth: 1–10 → A, 11–20 → B, 21–31 → C), Van Westendorp + NMS
 * for the everyday and ceremonial sets, Kano (6 features), brand routes,
 * channels and profile. Responses go to a new linked Google Sheet.
 *
 * HOW TO RUN
 * 1. Go to script.google.com → New project. Delete the sample code and
 *    paste this whole file.
 * 2. (Optional) Paste the Drive file IDs of your card images into CONFIG.
 *    Leave any blank and the script inserts a placeholder you replace by hand.
 * 3. Select the function buildTaruSurvey in the toolbar → Run.
 * 4. Approve the permissions. On a personal Gmail account Google shows
 *    "Google hasn't verified this app": click Advanced → Go to project → Allow.
 *    The script only touches your own Drive and Forms.
 * 5. Open View → Logs (or Execution log) for the form's edit link, live link
 *    and response sheet link. The form and sheet are moved into your
 *    taru-category-launch Drive folder.
 *
 * Re-running creates a NEW form. Delete the old one if you rebuild.
 */

const CONFIG = {
  FOLDER_ID: '1GxSGMFnib66p8F8CVTDZ3wpGGsQH1Che', // taru-category-launch Drive folder
  CARD_A: '',          // Drive file ID of Card A (control)
  CARD_B: '',          // Card B (certification)
  CARD_C: '',          // Card C (benefit + proof bundle)
  CARD_CEREMONIAL: '', // Neutral ceremonial card
  ROUTE_1: '',         // Brand route 1
  ROUTE_2: '',
  ROUTE_3: '',
};

const LIKELIHOOD = ['Definitely would', 'Probably would', 'Might or might not', 'Probably not', 'Definitely not'];
const AGREE = ['1 Strongly disagree', '2 Disagree', '3 Neutral', '4 Agree', '5 Strongly agree'];
const KANO = ["I'd like it", "I'd expect it", "I'm neutral", 'I can live with it', "I'd dislike it"];
const FEATURES = [
  'Certified organic fabric',
  'A QR code showing where the fabric came from',
  'A cut designed for fuller or mature builds',
  'Free alterations',
  'A comfort guarantee (return it if the fabric irritates)',
  'Styling help for the occasion',
];

function buildTaruSurvey() {
  const form = FormApp.create('What makes clothing trustworthy? (anonymous MBA study)');
  form.setDescription(
    'This anonymous survey is part of an independent MBA student study. It uses a fictional clothing brand ' +
    'and is not linked to any company. It takes about 9 minutes. We don\'t collect your name, phone or email, ' +
    'and answers are used only in summary form. By continuing, you agree to take part. You can stop at any time.'
  );
  form.setCollectEmail(false);
  form.setProgressBar(true);
  form.setAllowResponseEdits(false);
  form.setShowLinkToRespondAgain(false);
  form.setConfirmationMessage('Thank you. Your answers have been recorded. Sharing the survey with a father, uncle or relative who fits helps the study most.');

  // ---------- Page 1: consent ----------
  const consent = form.addMultipleChoiceItem()
    .setTitle('Do you agree to take part?')
    .setRequired(true);

  // ---------- Block A: screener ----------
  const pbAge = form.addPageBreakItem().setTitle('About you');
  const a1 = form.addMultipleChoiceItem().setTitle('A1. Your age band').setRequired(true);

  const pbRole = form.addPageBreakItem().setTitle('About you (continued)');
  const a2 = form.addMultipleChoiceItem().setTitle('A2. Which describes you?').setRequired(true);

  // ---------- Block B: purchase history (+ A3 city) ----------
  form.addPageBreakItem().setTitle('Your most recent ethnic-wear purchase')
    .setHelpText('If you have bought both for yourself and for your father or father-in-law, think of the most recent purchase.');
  form.addListItem().setTitle('A3. Your city').setRequired(true)
    .setChoiceValues(['Mumbai (incl. Thane, Navi Mumbai)', 'Pune', 'Bengaluru', 'Delhi NCR', 'Other metro (Chennai, Hyderabad, Kolkata, Ahmedabad)', 'Other city or town']);
  form.addMultipleChoiceItem().setTitle('B1. What was the occasion?').setRequired(true)
    .setChoiceValues(['Everyday or office', 'Festival', 'Wedding (as a guest)', 'Wedding in the family', 'Gift', 'Other']);
  form.addMultipleChoiceItem().setTitle('B2. How much did you spend per set?').setRequired(true)
    .setChoiceValues(['Under ₹2,000', '₹2,000–3,500', '₹3,500–6,000', '₹6,000–10,000', 'Above ₹10,000']);
  form.addMultipleChoiceItem().setTitle('B3. Where did you buy it?').setRequired(true)
    .setChoiceValues(['Brand store', 'Multi-brand store', 'Department store', 'Marketplace app (e.g. Myntra, Amazon)', 'Brand website', 'Tailor', 'Exhibition or pop-up']);
  form.addMultipleChoiceItem().setTitle('B4. Who decided what to buy?').setRequired(true)
    .setChoiceValues(['Me', 'Together with someone', 'Someone else']);

  // ---------- A4: day of birth → arm ----------
  form.addPageBreakItem().setTitle('One quick question')
    .setHelpText('This is used only to show you one of several versions of the next page.');
  const a4 = form.addListItem().setTitle('A4. Your day of birth (1–31)').setRequired(true);

  // ---------- Block C: three arms ----------
  const pbArmA = form.addPageBreakItem().setTitle('A product').setHelpText('Please look at this product card, then answer the questions below.');
  addImage_(form, CONFIG.CARD_A, 'Card A (control): "Made from natural fibres."');
  addClaimQuestions_(form);

  const pbArmB = form.addPageBreakItem().setTitle('A product').setHelpText('Please look at this product card, then answer the questions below.');
  addImage_(form, CONFIG.CARD_B, 'Card B (certification)');
  addClaimQuestions_(form);

  const pbArmC = form.addPageBreakItem().setTitle('A product').setHelpText('Please look at this product card, then answer the questions below.');
  addImage_(form, CONFIG.CARD_C, 'Card C (benefit + proof bundle)');
  addClaimQuestions_(form);

  // ---------- Block D: Van Westendorp + NMS ----------
  const pbD1 = form.addPageBreakItem().setTitle('Prices: the kurta set you just saw')
    .setHelpText('Think about the Everyday Kurta Set on the previous page. Enter amounts in rupees, numbers only (e.g. 3500).');
  addPriceQuestions_(form, '');

  form.addPageBreakItem().setTitle('Prices: a ceremonial set')
    .setHelpText('Now think about the ceremonial set below. Enter amounts in rupees, numbers only.');
  addImage_(form, CONFIG.CARD_CEREMONIAL, 'Ceremonial card (neutral, no claim)');
  addPriceQuestions_(form, ' (ceremonial set)');

  // ---------- Block E: Kano ----------
  form.addPageBreakItem().setTitle('What matters to you')
    .setHelpText('Two short grids about the same six features. The first asks how you would feel if the kurta set HAD each feature; the second, if it did NOT.');
  form.addGridItem().setTitle('E1. If the kurta set HAD each of these, how would you feel?')
    .setRows(FEATURES).setColumns(KANO).setRequired(true);
  form.addGridItem().setTitle('E2. If the kurta set did NOT have each of these, how would you feel?')
    .setRows(FEATURES).setColumns(KANO).setRequired(true);

  // ---------- Block F: brand routes ----------
  form.addPageBreakItem().setTitle('Three looks');
  addImage_(form, CONFIG.ROUTE_1, 'Look 1');
  addImage_(form, CONFIG.ROUTE_2, 'Look 2');
  addImage_(form, CONFIG.ROUTE_3, 'Look 3');
  form.addMultipleChoiceItem().setTitle("F1. Which of these three looks feels most like a brand you'd buy from?")
    .setChoiceValues(['Look 1', 'Look 2', 'Look 3']).setRequired(true);
  ['Look 1', 'Look 2', 'Look 3'].forEach(function (l) {
    form.addTextItem().setTitle('F2. One word for ' + l).setRequired(true);
  });

  // ---------- Block G: channels ----------
  form.addPageBreakItem().setTitle('Where you would buy');
  form.addCheckboxItem().setTitle('G1. Where would you expect to buy a brand like this? (Tick all that apply)')
    .setChoiceValues(['Brand store', 'Multi-brand or department store', 'Marketplace app (e.g. Myntra, Amazon)', 'Brand website', 'Exhibition or pop-up', 'Through a tailor', 'As a corporate or festive gift'])
    .setRequired(true);
  form.addScaleItem().setTitle('G2. How comfortable are you buying ethnic wear online?')
    .setBounds(1, 5).setLabels('Not at all comfortable', 'Very comfortable').setRequired(true);
  form.addMultipleChoiceItem().setTitle('G3. When buying online, how many sizes would you order to try?')
    .setChoiceValues(['1', '2', '3 or more']).setRequired(true);
  form.addMultipleChoiceItem().setTitle('G4. Would you pay online in advance or on delivery?')
    .setChoiceValues(['Pay online in advance', 'Pay on delivery']).setRequired(true);

  // ---------- Block H: profile ----------
  form.addPageBreakItem().setTitle('Last question');
  form.addMultipleChoiceItem().setTitle('H1. Annual household income (optional)')
    .setChoiceValues(['Under ₹10 lakh', '₹10–25 lakh', '₹25–50 lakh', '₹50 lakh–1 crore', 'Above ₹1 crore', 'Prefer not to say'])
    .setRequired(false);

  // ---------- Branching (set after all pages exist) ----------
  consent.setChoices([
    consent.createChoice('I agree', FormApp.PageNavigationType.CONTINUE),
    consent.createChoice('I do not agree', FormApp.PageNavigationType.SUBMIT),
  ]);
  a1.setChoices([
    a1.createChoice('Under 18', FormApp.PageNavigationType.SUBMIT),
    a1.createChoice('18–24', FormApp.PageNavigationType.CONTINUE),
    a1.createChoice('25–32', FormApp.PageNavigationType.CONTINUE),
    a1.createChoice('33–39', FormApp.PageNavigationType.CONTINUE),
    a1.createChoice('40–49', FormApp.PageNavigationType.CONTINUE),
    a1.createChoice('50–60', FormApp.PageNavigationType.CONTINUE),
    a1.createChoice('61 or older', FormApp.PageNavigationType.CONTINUE),
  ]);
  a2.setChoices([
    a2.createChoice("I'm a man aged 40–60 and bought Indian ethnic wear (kurta, kurta set, Nehru jacket, sherwani) for myself in the last 2 years", FormApp.PageNavigationType.CONTINUE),
    a2.createChoice('I bought ethnic wear for my father or father-in-law in the last 2 years', FormApp.PageNavigationType.CONTINUE),
    a2.createChoice('Both', FormApp.PageNavigationType.CONTINUE),
    a2.createChoice('Neither', FormApp.PageNavigationType.SUBMIT),
  ]);
  const days = [];
  for (let d = 1; d <= 31; d++) {
    const target = d <= 10 ? pbArmA : (d <= 20 ? pbArmB : pbArmC);
    days.push(a4.createChoice(String(d), target));
  }
  a4.setChoices(days);
  // After arm A and arm B, skip the remaining arms and go straight to Block D.
  pbArmB.setGoToPage(pbD1);
  pbArmC.setGoToPage(pbD1);

  // ---------- Response sheet + move into Drive folder ----------
  const ss = SpreadsheetApp.create('TARU survey responses');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());
  try {
    const folder = DriveApp.getFolderById(CONFIG.FOLDER_ID);
    DriveApp.getFileById(form.getId()).moveTo(folder);
    DriveApp.getFileById(ss.getId()).moveTo(folder);
  } catch (e) {
    Logger.log('Could not move files into the folder (check FOLDER_ID): ' + e);
  }

  Logger.log('EDIT the form:    ' + form.getEditUrl());
  Logger.log('LIVE link:        ' + form.getPublishedUrl());
  Logger.log('Response sheet:   ' + ss.getUrl());
}

/** Block C questions, identical in every arm. */
function addClaimQuestions_(form) {
  form.addGridItem()
    .setTitle('C1–C3. How much do you agree with each statement about this product?')
    .setRows([
      'C1. I believe what this product says about itself.',
      'C2. This brand seems honest about how its clothes are made.',
      "For this row, please select '2 Disagree'.", // attention check
      "C3. I'd trust this brand for an important occasion.",
    ])
    .setColumns(AGREE)
    .setRequired(true);
  form.addMultipleChoiceItem().setTitle('C4. How likely are you to buy this?')
    .setChoiceValues(LIKELIHOOD).setRequired(true);
  form.addMultipleChoiceItem().setTitle("C5. Compared with a Manyavar kurta set you'd consider, would you pay:")
    .setChoiceValues(['Less', 'About the same', 'Up to 10% more', '10–25% more', 'More than 25% more'])
    .setRequired(true);
}

/** Block D questions: 4 Van Westendorp prices + 2 NMS likelihoods. */
function addPriceQuestions_(form, suffix) {
  const v = FormApp.createTextValidation()
    .requireNumberBetween(1, 500000)
    .setHelpText('Please enter a number in rupees, e.g. 3500')
    .build();
  [
    "D1. At what price would this be so cheap that you'd doubt its quality?",
    'D2. At what price would it be a bargain, a great buy for the money?',
    'D3. At what price would it start to feel expensive, but still worth considering?',
    'D4. At what price would it be too expensive to consider?',
  ].forEach(function (t) {
    form.addTextItem().setTitle(t + suffix).setValidation(v).setRequired(true);
  });
  form.addMultipleChoiceItem().setTitle('D5. At the "bargain" price you gave, how likely are you to buy?' + suffix)
    .setChoiceValues(LIKELIHOOD).setRequired(true);
  form.addMultipleChoiceItem().setTitle('D6. At the "expensive" price you gave, how likely are you to buy?' + suffix)
    .setChoiceValues(LIKELIHOOD).setRequired(true);
}

/** Adds an image from Drive, or a visible placeholder if no ID is set. */
function addImage_(form, fileId, label) {
  if (fileId) {
    try {
      const blob = DriveApp.getFileById(fileId).getBlob();
      form.addImageItem().setImage(blob).setTitle('');
      return;
    } catch (e) {
      Logger.log('Could not load image for ' + label + ': ' + e);
    }
  }
  form.addSectionHeaderItem().setTitle('[INSERT IMAGE HERE: ' + label + ']')
    .setHelpText('Placeholder added by the build script. Replace with the image in the Forms editor, then delete this block.');
}

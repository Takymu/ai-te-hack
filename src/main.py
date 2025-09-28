from pdftotext import extract_text_from_pdf
from comixgen import generate_comix
from scenparser import parse_scenario
from diffusion import generate_image

doctext = extract_text_from_pdf('../data/Памятка ОБРАЩЕНИЯ ГРАЖДАН в прокуратуру.pdf')

GENERATE_SCENARIO = False

scenario = None

if GENERATE_SCENARIO:
    with open('scenariopamatka.txt', 'r', encoding='utf-8') as file:
        scenario = file.read()
else:
    scenario = generate_comix(doctext)

scenes_count = scenario.count('[scene]')

scenario = parse_scenario(scenario)

charLdesc = scenario['charLdesc'][0]
charRdesc = scenario['charRdesc'][0]


for i in range(scenes_count):
    scenedesc = scenario['scenes'][i]
    charLaction = scenario['charLaction'][i]
    charRaction = scenario['charRaction'][i]

    print(f'scenedesc:\n{scenedesc}\n')

    print(f'charLaction:\n{charLaction}\n')
    print(f'charRaction:\n{charRaction}\n')


    sceneprompt = f'''
        {scenedesc}
        It's a part of comic book with characters in the Marvel style, draw full-length characters.
        The characters should be cartoony, 2D, suitable for a comic, and not overly complex.
    '''
    if charLaction is not None:
        sceneprompt += 'Appearance of left character:\n' + charLdesc + '\n'
    
    if charRaction is not None:
        sceneprompt += 'Appearance of right character:\n' + charRdesc + '\n'

    img, ext = generate_image(sceneprompt)
    print(ext)
    print(sceneprompt)
    with open('f1'+ext, 'wb') as f:
        f.write(img)

    break

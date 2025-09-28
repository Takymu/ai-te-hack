from pdftotext import extract_text_from_pdf
from comixgen import generate_comix
from scenparser import parse_scenario

doctext = extract_text_from_pdf('../data/Памятка ОБРАЩЕНИЯ ГРАЖДАН в прокуратуру.pdf')

# scenario = generate_comix(doctext)
scenario = None
with open('scenariopamatka.txt', 'r', encoding='utf-8') as file:
    scenario = file.read()

scenes_count = scenario.count('[scene]')

scenario = parse_scenario(scenario)

charLdesc = scenario['charLdesc'][0]
charLdesc = scenario['charRdesc'][0]


for i in range(scenes_count):
    scenedesc = scenario['scenes'][i]
    charLaction = scenario['charLaction'][i]
    charRaction = scenario['charRaction'][i]

    print(f'scenedesc:\n{scenedesc}\n')

    print(f'charLaction:\n{charLaction}\n')
    print(f'charRaction:\n{charRaction}\n')

    if charLaction is None:
        

    sceneprompt = f'''
        {scenedesc}
    '''

from pdftotext import extract_text_from_pdf
from scenparser import parse_scenario
# from diffusion import generate_image
from gigachat import generate_image

from actor_critic import generate_comix_actcrit
from yolo_detect import detect_faces
from addovals import add_speech_bubble
from imgcombine import combine_images_to_file

doctext = extract_text_from_pdf('../data/_Уведомление_об_отказе_в_приеме_и_регистрации_заявления_ВУ-20250923-13521150876-1-1.pdf')

GENERATE_SCENARIO = True

scenario = None

if GENERATE_SCENARIO:
    scenario = generate_comix_actcrit(doctext)
else:
    with open('scenariopamatka.txt', 'r', encoding='utf-8') as file:
        scenario = file.read()

scenario = parse_scenario(scenario)

charLdesc = scenario['charLdesc'][0]
charRdesc = scenario['charRdesc'][0]

scenelist = []

for i in range(len(scenario['scenes'])):
    scenedesc = scenario['scenes'][i]
    charLaction = scenario['charLaction'][i]
    charRaction = scenario['charRaction'][i]

    sceneprompt = f'''
        {scenedesc}
        '''
    #!     It's a part of comic book with characters in the comix style, draw full-length characters.
    #!     The characters should be cartoony, 2D, suitable for a comic, and not overly complex and not overly expressive.
    #! '''
    if charLaction is not None:
        sceneprompt += 'Appearance of left character:\n' + charLdesc + '\n'
    
    if charRaction is not None:
        sceneprompt += 'Appearance of right character:\n' + charRdesc + '\n'

    sceneprompt += 'location is absent of people'

    img, ext = generate_image(sceneprompt)
    print(sceneprompt)
    faces = detect_faces(img)
    left = True

    if len(faces) == 2 and faces[0][0] > faces[1][0]:
        face = faces[0]
        faces[0] = faces[1]
        faces[1] = face

    for x, y in faces:
        if left and charLaction is not None:
            img = add_speech_bubble(img, charLaction, x, y,
                               max_bubble_width=280,
                                 min_font_size=8)
            left = False
        elif charRaction is not None:
            img = add_speech_bubble(img, charRaction, x, y,
                               max_bubble_width=280,
                                 min_font_size=8)
    scenelist.append(img)


imgname = 'comix.jpg'
combine_images_to_file(scenelist, imgname)
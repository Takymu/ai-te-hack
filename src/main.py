from pdftotext import extract_text_from_pdf
from scenparser import parse_scenario
from diffusion import generate_image
# from gigachat import generate_image

from actor_critic import generate_comix_actcrit
from yolo_detect import detect_faces, detect_faces_full
from addovals import add_speech_bubbles_multiple
from imgcombine import combine_images_to_file

doctext = extract_text_from_pdf('../data/Правила записи иа первичный прием, ЦПК ФТС.pdf')

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
        It's a part of comic book with characters in the comix style, draw full-length characters.
        The characters should be cartoony, 2D, suitable for a comic, and not overly complex and not overly expressive.
        '''
    if charLaction is not None:
        sceneprompt += 'Appearance of left character:\n' + charLdesc + '\n'
    
    if charRaction is not None:
        sceneprompt += 'Appearance of right character:\n' + charRdesc + '\n'

    sceneprompt += 'location is absent of people'

    img, ext = generate_image(sceneprompt)
    print(sceneprompt)
    faces = detect_faces_full(img)
    left = True

    if len(faces) == 2 and faces[0][0] > faces[1][0]:
        face = faces[0]
        faces[0] = faces[1]
        faces[1] = face

    bubels = []
    UP_HEAD = 0
    for x1, y1, x2, y2 in faces:
        x = (x1+x2)//2
        y = (y1+y2)//2
        UP_HEAD += y

        if left and charLaction is not None:
            bubels.append({
                "text": charLaction,
                "head_coords": (x, y)
            })
            left = False
        elif charRaction is not None:
            bubels.append({
                "text": charRaction,
                "head_coords": (x, y)
            })

    UP_HEAD //= len(faces)

    add_speech_bubbles_multiple(
        img, bubels,
        MAX_BUBBLE_WIDTH=280,
        MIN_FONT_SIZE=8,
        BORDER_COLOR = "black",
        FILL_COLOR = "white",
        TEXT_COLOR = "black",
        BORDER_WIDTH = 3,
        UP_HEAD=UP_HEAD,
        RATIO_HEAD=0.5,
        RATIO_ELLIPSE=0.5
    )
    scenelist.append(img)


imgname = 'comics.jpg'
combine_images_to_file(scenelist, imgname)

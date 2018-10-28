# das is die Datei in der ich Sachen implementiere (also ich bin Philip, duh)
from PIL import Image, ImageDraw
from functools import wraps

colors = {
    'b': (0, 0, 0),
    'w': (255, 255, 255),
    None: (255, 0, 0)
}

def draw_carpet(bot, update, carpet, pixthick):
    hght = len(carpet) * pixthick
    wdth = len(carpet[0]) * pixthick
    #bot.send_message(update.message.chat_id, text=str(hght)+' '+str(wdth))
    img = Image.new('RGB', (wdth, hght),(0,0,0,255))
    pixels = img.load()
    for by in range(len(carpet)):           # pic y
        for bx in range(len(carpet[0])):    # pic x
            for sy in range(pixthick) :     # pix y
                for sx in range(pixthick):  # pix x
                    y = by*pixthick+sy
                    x = bx*pixthick+sx
                    if carpet[by][bx] == 0: col = colors['w']
                    if carpet[by][bx] == 1: col = colors['b']
                    if carpet[by][bx] == 2: col = colors['b']
                    if carpet[by][bx] == 3: col = colors['w'] 
                    pixels[x,y] = col

    img.save('carpet.png')
    bot.send_photo(update.message.chat_id, open('carpet.png', 'rb'))


def philip_carpet(bot,update,args):
    pix = int(float(args.pop(0)))
    depth = int(float(args.pop(0)))
    if depth > 4: return false
    wdt = int(float(args.pop(0)))
    hgt = int(float(args.pop(0)))
    if len(args) != wdt*hgt:
        bot.send_message(update.message.chat_id, text="Angaben nicht valide")
        return 
    base = [[0 for x in range(wdt)] for y in range(hgt)] # wie Text: Zeilen, und in diesen Buchstaben
    carp = [[0 for x in range(wdt)] for y in range(hgt)] # ich bin ein Karpfen
    for y in range(hgt):
        for x in range(wdt):
            base[y][x] = int(float(args[0]))
            carp[y][x] = int(float(args.pop(0)))
            # 0 -> leer
            # 1 -> Muster
            # -1 -> invertiertes Muster
            # 2 -> gefüllt
    for r in range(depth):
        carp = recursive_carpet(carp, base)
    '''s = ''
    for y in range(len(carp)):
        s = s + "`"
        for x in range(len(carp[0])):
            s = s+''+str(carp[y][x])+""
        s = s+"`\n"
    bot.send_message(update.message.chat_id, text=s, parse_mode='Markdown')'''
    draw_carpet(bot, update, carp, pix)

def carpet_modify(mod, num):
    # hab kp wie ich das unhardcodig machen soll
    if mod == 0:
        return 0
    elif mod == 2:
        return 2
    elif mod == 1:
        return num
    elif mod == 3:
        if num == 1: return 3
        elif num == 3: return 1
        elif num == 2: return 0
        elif num == 0: return 2
    

def recursive_carpet(carp, base):
    bw = len(base[0])
    bh = len(base)
    cw = len(carp[0])
    ch = len(carp)

    ret = [[0 for x in range(bw*cw)] for y in range(bh*ch)]
    for ly in range(ch):                # l = large
        for lx in range(cw):
            mod = carp[ly][lx]          # mod = modifier
            for sy in range(bh):        # s = small
                for sx in range(bw):
                    y = ly*bh+sy
                    x = lx*bw+sx
                    num = base[sy][sx]
                    ret[y][x] = carpet_modify(mod, num)
    return ret

def philip_math(bot,update,args):
    # is the operand valid?
    arg = args.pop(0)
    if arg == '+': res = 0
    elif arg == '*': res = 1
    else: 
        bot.send_message(update.message.chat_id, text="kein valider Operator")
        return 

    # are all numbers really numbers?
    try:
        for x in range(len(args)): 
            y = float(args[x])
            if arg == '+': res += y
            elif arg == '*': res *= y
    except ValueError:
        bot.send_message(update.message.chat_id, text="keine validen Zahlen")
        return
    bot.send_message(update.message.chat_id, text=str(res))   


    

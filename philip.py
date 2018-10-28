# das is die Datei in der ich Sachen implementiere

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

    
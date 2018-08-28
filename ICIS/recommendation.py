def milkpowder(user_milkpowder):
    import pandas as pd
    import random
    milkPowder_rec = pd.read_csv('rec_milkPowder.csv')

    milkPowder_rec.drop(milkPowder_rec.columns[milkPowder_rec.columns.str.contains('unnamed',case = False)],axis = 1, inplace=True)

    pref_milk = user_milkpowder
    milk_pref_list = []

    new = milkPowder_rec[milkPowder_rec['title'].str.contains(str(pref_milk))]
    if random.random() <0.5:
        milk_pref_list.append(new.iloc[random.randrange(0,len(new)),0])
    else:
        milk_pref_list.append(new.iloc[random.randrange(0,len(new)),0])
        milk_pref_list.append(new.iloc[random.randrange(0,len(new)),0])
    if len(milk_pref_list) == 1:
        for i in range(3):
            num = milkPowder_rec[milkPowder_rec['title'].str.contains(pref_milk)].replyCount.nlargest(1).index[0]
            milk_pref_list.append(milkPowder_rec.iloc[num,5:8][i])
    else:
        for i in range(2):
            num = milkPowder_rec[milkPowder_rec['title'].str.contains(pref_milk)].replyCount.nlargest(1).index[0]
            milk_pref_list.append(milkPowder_rec.iloc[num,5:7][i])

    return milk_pref_list[random.randrange(0, 3)]


def diaper(user_diaper):
    import pandas as pd
    import random
    diaper_rec = pd.read_csv('rec_diaper.csv')

    diaper_rec.drop(diaper_rec.columns[diaper_rec.columns.str.contains('unnamed', case=False)], axis=1, inplace=True)

    pref_diaper = user_diaper
    diaper_pref_list = []
    new = diaper_rec[diaper_rec['title'].str.contains(str(pref_diaper))]
    if random.random() < 0.5:
        diaper_pref_list.append(new.iloc[random.randrange(0, len(new)), 0])
    else:
        diaper_pref_list.append(new.iloc[random.randrange(0, len(new)), 0])
        diaper_pref_list.append(new.iloc[random.randrange(0, len(new)), 0])
    if len(diaper_pref_list) == 1:
        for i in range(3):
            num = diaper_rec[diaper_rec['title'].str.contains(pref_diaper)].replyCount.nlargest(1).index[0]
            diaper_pref_list.append(diaper_rec.iloc[num, 5:8][i])
    else:
        for i in range(2):
            num = diaper_rec[diaper_rec['title'].str.contains(pref_diaper)].replyCount.nlargest(1).index[0]
            diaper_pref_list.append(diaper_rec.iloc[num, 5:7][i])

    return diaper_pref_list[random.randrange(0, 3)]


def toy(user_toy):
    import pandas as pd
    import random

    toy_rec = pd.read_csv('rec_toy.csv')

    toy_rec.drop(toy_rec.columns[toy_rec.columns.str.contains('unnamed', case=False)], axis=1, inplace=True)

    pref_toy = user_toy
    toy_pref_list = []
    new = toy_rec[toy_rec['title'].str.contains(str(pref_toy))]
    if random.random() < 0.5:
        toy_pref_list.append(new.iloc[random.randrange(0, len(new)), 0])
    else:
        toy_pref_list.append(new.iloc[random.randrange(0, len(new)), 0])
        toy_pref_list.append(new.iloc[random.randrange(0, len(new)), 0])
    if len(toy_pref_list) == 1:
        for i in range(3):
            num = toy_rec[toy_rec['title'].str.contains(pref_toy)].replyCount.nlargest(1).index[0]
            toy_pref_list.append(toy_rec.iloc[num, 5:8][i])
    else:
        for i in range(2):
            num = toy_rec[toy_rec['title'].str.contains(pref_toy)].replyCount.nlargest(1).index[0]
            toy_pref_list.append(toy_rec.iloc[num, 5:7][i])

    return toy_pref_list[random.randrange(0, 3)]


def snack(user_snack):
    import pandas as pd
    import random

    snack_rec = pd.read_csv('rec_snack.csv')

    snack_rec.drop(snack_rec.columns[snack_rec.columns.str.contains('unnamed', case=False)], axis=1, inplace=True)

    pref_snack = user_snack
    snack_pref_list = []
    new = snack_rec[snack_rec['title'].str.contains(str(pref_snack))]
    if random.random() < 0.5:
        snack_pref_list.append(new.iloc[random.randrange(0, len(new)), 0])
    else:
        snack_pref_list.append(new.iloc[random.randrange(0, len(new)), 0])
        snack_pref_list.append(new.iloc[random.randrange(0, len(new)), 0])
    if len(snack_pref_list) == 1:
        for i in range(3):
            num = snack_rec[snack_rec['title'].str.contains(pref_snack)].replyCount.nlargest(1).index[0]
            snack_pref_list.append(snack_rec.iloc[num, 5:8][i])
    else:
        for i in range(2):
            num = snack_rec[snack_rec['title'].str.contains(pref_snack)].replyCount.nlargest(1).index[0]
            snack_pref_list.append(snack_rec.iloc[num, 5:7][i])

    return snack_pref_list[random.randrange(0, 3)]
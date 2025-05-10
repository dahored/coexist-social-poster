def join_array(list_items):
    """
    Une una lista de hashtags en un solo string separados por espacios.
    Ejemplo:
        ["#AmorIncondicional", "#ValentíaEnElAmor"] → "#AmorIncondicional #ValentíaEnElAmor"
    """
    return " ".join(list_items)

def split_array(string_value):
    """
    Convierte un string de hashtags separados por espacios en una lista.
    Ejemplo:
        "#Amor #Valentía #Coraje" → ["#Amor", "#Valentía", "#Coraje"]
    """
    return [tag.strip() for tag in string_value.strip().split() if tag.strip()]

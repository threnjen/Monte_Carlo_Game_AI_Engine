import PySimpleGUI as sg

# First the window layout in 2 columns


# file_list_column = [
#     [
#         sg.Text("Image Folder"),
#         sg.In(size=(1, 1), enable_events=True, key="-FOLDER-"),
#         sg.FolderBrowse(),
#     ],
#     [
#         sg.Listbox(
#             values=[], enable_events=True, size=(40, 20), key="-FILE LIST-"
#         )
#     ],
# ]

# # For now will only show the name of the file that was chosen
# image_viewer_column = [
#     [sg.Text("Choose an image from list on left:")],
#     [sg.Text(size=(40, 1), key="-TOUT-")],
#     [sg.Image(key="-IMAGE-")],
# ]

def display_factory(factory_dict: dict):
    factory_prefix = "fact_"
    sg_col_array = []
    for disp_num, tile_dict in factory_dict.items():
        tile_array = [sg.Text(f"Factory {disp_num}: ")]
        for tile, color in tile_dict.items():
            tile_array.append(sg.Button(
                '  ', button_color=color, key=f"{factory_prefix}{disp_num}{color}_{tile}"))

        # tiles = [[sg.Button('  ', button_color=tile_dict[0], key=f"{factory_prefix}{disp_num}{tile_dict[0]}_0"),
        #           sg.Button(
        #               '  ', button_color=tile_dict[1], key=f"{factory_prefix}{disp_num}{tile_dict[1]}_1"), ],
        #          [sg.Button('  ', button_color=tile_dict[2], key=f"{factory_prefix}{disp_num}{tile_dict[2]}_2"),
        #          sg.Button(
        #              '  ', button_color=tile_dict[3], key=f"{factory_prefix}{disp_num}{tile_dict[3]}_3"), ]]
        sg_col_array.append(tile_array)

    return sg_col_array


def container(tile_dict: dict, label: str, prefix: str):
    sg_col_array = [sg.Text(f"{label}: ")]
    for tile, count in tile_dict.items():
        for i in range(count):
            sg_col_array.append(
                sg.Button('   ', button_color=tile, key=f"{prefix}{tile}_{i}"))
    return sg_col_array


def star(color: str, pos_dict: dict, player: str):
    prefix = 'star'
    star_array = [sg.Text(f"{color} star")]
    for pos, occupied in pos_dict.items():
        if occupied:
            if color == "all":
                b_color = "white"
            else:
                b_color = color
        else:
            b_color = "gray"
        star_array.append(
            sg.Button(f' {pos} ', button_color=b_color, key=f"{prefix}_{player}_{color}_{pos}"))
    return star_array


def display_stuff(factory_dict: dict, supply_dict: dict, player_dict: dict, player_stars: dict, legal_moves: dict, score_dict: dict):
    fact_layout = []
    for fact, fact_tiles in factory_dict.items():
        if fact == -1:
            label = "Center:  "
        else:
            label = f"Factory {fact}:  "
        fact_layout.append(
            container(fact_tiles, label, f"fact_{fact}_"))
    supply_layout = container(supply_dict, "Supply:  ", "supply_")

    player_layout = []
    for player, player_tiles in player_dict.items():

        player_layout.append(
            container(player_tiles, f"Player {player}: ", f"player_{player}"))
        player_layout.append([sg.Text(f"Score: {score_dict[player]}")])
        for color, pos_dict in player_stars[player].items():
            player_layout.append(star(color, pos_dict, player))

    # ----- Full layout -----
    layout = [
        fact_layout,
        [supply_layout],
        player_layout
    ]

    window = sg.Window("Image Viewer", layout)

    window.Finalize()

    while True:
        event, values = window.read()
        for index, action in legal_moves.items():
            try:
                if action[-1] in event:
                    window.close()
                    return index
            except KeyError:
                pass
        if event == "Exit" or event == sg.WIN_CLOSED:
            return 0

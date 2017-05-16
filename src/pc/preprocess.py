import pandas as pd
import os
import random

# DATA_DIR = r'C:\Users\hawker\Dropbox\Public\data_intake'
DATA_DIR = 'C:/users/Wojtek/Dropbox/data_intake/'


def filter_split_data(df, move_ratio=0.5, index_min=100, index_max=250):
    df['filtered'] = ((df.index > index_min) & (
        df.index <= index_max) & (~pd.isnull(df['w']))).astype(bool)
    move_ids = df[(df['w'] | df['s'] | df['a'] | df['d'])
                  & df['filtered']].index

    index_min = move_ids[0]  # set indices to first & last frame with move
    index_max = move_ids[-1]

    non_move_count = round(2 * len(move_ids) * (1 - move_ratio))
    non_move_ids = set(df[df['filtered']].index) - set(move_ids)
    non_move_ids = [non_move_id for non_move_id in non_move_ids if (
        (non_move_id > 0.9 * index_min) & (non_move_id < 1.1 * index_max))]
    if len(non_move_ids) > non_move_count:
        non_move_ids = random.sample(non_move_ids, non_move_count)

    df['filtered'] = False
    df.set_value(move_ids, 'filtered', True)
    df.set_value(non_move_ids, 'filtered', True)
    return df


if __name__ == '__main__':
    file_name = "steering_v1.csv"

    data_folders = [data_folder for data_folder in os.listdir(
        DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, data_folder))]
    data_folders = data_folders[:16]

    total = 0
    for data_folder in data_folders:
        df = pd.read_csv((DATA_DIR + '/' + data_folder + "/" + file_name))
        df = filter_split_data(df, move_ratio=0.5)

        total += sum(df['filtered'])
        df.to_csv((DATA_DIR + '/' + data_folder + "/steering_filtered.csv"))

    print(total)

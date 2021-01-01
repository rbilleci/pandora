from logging import basicConfig, INFO
import data.oxford_data

basicConfig(level=INFO, format='%(asctime)s\t%(levelname)s\t%(filename)s\t%(message)s')

data.oxford_data.update()

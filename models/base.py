from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import json
import io

with io.open(".\\config.json", "r", encoding="utf-8") as json_data_file:
    data = json.load(json_data_file)

engine = create_engine(data['Connection-String'], max_overflow = -1)
Session = sessionmaker(bind = engine)

Base = declarative_base()
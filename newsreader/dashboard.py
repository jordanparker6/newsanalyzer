from sqlmodel import default
import streamlit as st
import pandas as pd
import argparse
import datetime as dt
from newsreader.database import Database

parser = argparse.ArgumentParser(description="A steamlit dashboard for visualising news analytics.")
parser.add_argument("--database", type=str, default="sqlite:///database.db")

class Dasboard:
    def __init__(self, database) -> None:
        self.db = Database(database)
        self.attr = {
            "date_range": self.get_date_range(),
        }
        self.state = st.session_state
        self.build()


    def build(self):

        # ~~~ Build Sidebar ~~~~~~~~~
        st.sidebar.header("Newsreader")

        with st.form(key="date_picker"):
            st.sidebar.date_input(
                "Period From",
                key="period_from",
                min_value=self.attr["date_range"][0],
                max_value=self.attr["date_range"][1],
                value=self.attr["date_range"][0]
            )
            st.sidebar.date_input(
                "Period To",
                key="period_to",
                min_value=self.attr["date_range"][0],
                max_value=self.attr["date_range"][1],
                value=self.attr["date_range"][1]
            )

        # ~~~ Build Main UI ~~~~~~~~~~

        st.text_input("Search")

        st.write([self.state.period_from, self.state.period_to])
        st.write(self.get_total_sentiment("00375cd420e37d4084c6668975f91648"))


    # ~~~ Callbacks ~~~~~~~~~~~
        

    # ~~~ Analytics Operations ~~~~~~

    def get_date_range(self):
        ans = self.db.exec("""
            SELECT MIN(date) as first_date, MAX(date) as last_date FROM document
        """)
        return list(map(dt.datetime.fromisoformat, ans[0]))

    def get_total_sentiment(self, document_id: str):
        ans = self.db.exec("""
            WITH t1 AS (
                SELECT 
                document.id as document_id, 
                paragraph.sentiment as sent,  
                COUNT(*) as paragraphs
                FROM document
                JOIN paragraph ON document.id = paragraph.document_id
                WHERE document.id = :document_id
                GROUP BY document.id, paragraph.sentiment
            )
            SELECT sent, paragraphs FROM t1
        """, params={ "document_id": document_id })
        return pd.DataFrame(ans, columns=["lable", "total_paragraphs"])
  

if __name__ == "__main__":
    args = parser.parse_args()
    dashboard = Dasboard(args.database)
    dashboard.get_total_sentiment("00375cd420e37d4084c6668975f91648")

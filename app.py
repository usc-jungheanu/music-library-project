import streamlit as st
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="Music App",
        page_icon="👋",
    )

    st.write("# TuneSync: Music Database Manager 🎶")

st.text('Fixed width text')

st.markdown('_Markdown_') # see #*

st.caption('Balloons. Hundreds of them...')

st.latex(r''' e^{i\pi} + 1 = 0 ''')

st.write('Most objects') # df, err, func, keras!

st.write(['st', 'is <', 3]) # see *

st.title('My title')

st.header('Jason Ungheanu')

st.subheader('My sub')

st.code('for i in range(8): foo()')

# * optional kwarg unsafe_allow_html = True


if __name__ == "__main__":
    run()

def show():
    import streamlit as st
    from streamlit_extras.colored_header import colored_header

    image_logo = "HySPI.png"

    # Create a layout with two columns
    col1, col2 = st.columns(2)

    # Place the image in the first column and align it to the center
    col1.image(image_logo, width=300, caption='', )

    st.markdown("# Industrial&nbsp;Hydrogen")
    st.markdown("### Prospective Scenarios of Environmental Impacts")
    st.markdown("ISIGE, O.I.E and PSI")
    colored_header(
        label="",
        description="",
        color_name="blue-70",
    )

    st.write('''
    The HySPI project aims to develop protocols and tools for holistically, multi-criteria, and prospectively analyzing the environmental impacts of industrial hydrogen (H2) value chains in France, from production to on-site usage, including storage and distribution. To achieve this, prospective Life Cycle Assessment (LCA) methods, both attributional and consequential, will be employed.

    This approach will help fill the gap in holistic studies available on the environmental impacts of hydrogen production and industrial usage chains, offering a multi-criteria view across the entire life cycle, taking into account potential shifts in environmental burdens between value chain stages or different impact categories.

    The developed tools and protocols will consider potential technological advancements in H2, particularly in the electrolysis domain. Parametric models will be created to easily assess the effects of these technological advancements on environmental impacts.

    In addition to the traditional attributional LCA method, HySPI will develop a consequential protocol to evaluate environmental impacts considering various hydrogen deployment scenarios. These scenarios are based on public planning (SNBC, national strategy for hydrogen in France), prospective developments by energy actors and environmental agencies (RTE, ADEME), as well as scientific literature on prospective modeling.

    The main objective of HySPI is not to provide detailed inventories of the various industrial H2 usage chains in France, but to create an environment that enables industry professionals and LCA stakeholders to apply attributional, consequential, and prospective LCA methods to different case studies.
    ''')
    # Authors
    st.markdown("---")
    st.write("Authors of this data package:")
    st.write("- Juliana Steinbach (juliana.steinbach@minesparis.psl.eu)")
    st.write("- Joanna Schlesinger (joanna.schlesinger@minesparis.psl.eu)")
    st.write("- Thomas Beaussier (thomas.beaussier@minesparis.psl.eu)")
    st.write("- Paula Perez-Lopez (paula.perez_lopez@minesparis.psl.eu)")
    st.write("- Romain Sacchi (romain.sacchi@psi.ch)")


if __name__ == "__main__":
    show()
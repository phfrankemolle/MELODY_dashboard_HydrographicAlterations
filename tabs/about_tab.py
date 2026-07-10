import streamlit as st
def about():
  st.header("About MELODY (and MELODY maps)")
  st.write("MELODY is een research project uitgevoerd aan e Universeit Twente. De afkorting staat voor ModEling LOwer Shoreface Seabed DYnamics for a climate-proof coast, en heeft funding van de NWO. Het MELODY-project focust op beter begrip van morphodynamica aan de diepe vooroever. De diepe vooroever valt samen met de zone waarin golven oplopen en vervormen, wat in het engels 'shoaling' wordt genoemd.")
  
  st.header("MELODY MAPS")
  st.write("MELODY maps is onderdeel van een EngD-project (Engineering Doctorate) waar de invloed van offshore wind turbines en zandputten op hydrodynamica op zee en dichter bij de kust centraal staan. Het dashboard is gemaakt in samenwerking met Rijkswaterstaat om te kijken naar mogelijke kritieke prestatie indicatoren (KPI) om hydrografische veranderingen te kwantificeren. In het dashboard ligt de focus op residuele stromingen aan de zeebodem, saliniteit en temperatuur. Er wordt gekeken naar drie scenario's: het referentie scenario: de bodem en windparken zoals ze waren in 2012, de verwachte situatie in 2027 en een mogelijk toekomstscenario voor 2040. Vervolgens kun je de (relatieve) verschillen tussen een scenario en het referentiescenario laten zien en experimenteren met polygons voor verschillende drempelwaardes (bijv. een polygon voor een relatieve verandering van de residuele snelheid >10%) om de invloeden te bestuderen. \n Disclaimer: De huidige versie neemt de effecten van zandputten nog niet mee.")
  
  st.header("Waar komt de data vandaan?")
  st.write("Het dashboard haalt data uit openbaar toegankelijke datasets (bathymetrie van GEBCO, wind turbine locaties via NSEC, en sommige tijdsreeksen van RWS waterinfo) en is deels gemodelleerd. Saliniteit, temperatuur en residuele stromingen worden berekend via een aangepaste versie van het 3D Dutch Continental Shelf Model met een variabel grid (3D DCSM-FM), dat wordt geforceerd met getij, windvelden, zonnestraling, temperatuur en saliniteit, maar zonder de invloed van zeespiegelstijging. Wind turbines worden toegevoegd aan het model door de schuifspanning door de wind aan het oppervlakte te veranderen. De forceringsdata is voor alle scenarios gekozen als de situatie in Juli 2013 en geeft bruikbare resultaten over de tijdspan van twee spring- en doodtij cycli. Deze worden vervolgens gemiddeld over de tijd en verwerkt tot kaarten.")
 
  st.markdown(
      "Wil je meer weten over het MELODY project? Ga dan naar "
      "[https://melody-research.nl"
  )


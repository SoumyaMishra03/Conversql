def schema_entity_recognizer(tokens, schema_terms, synonym_map=None):
    if synonym_map is None:
        synonym_map = {
    "asteroid":                       "asteroids",
    "asteroids":                      "asteroids",
    "asteroiddb":                     "asteroids",
    "asteroidsdb":                    "asteroids",

    # columns
    "id":                             "id",
    "asteroidid":                     "id",
    "name":                           "name",
    "asteroidname":                   "name",
    "absolutemagnitude":              "absolute magnitude",
    "absolutemag":                    "absolute magnitude",
    "mag":                            "absolute magnitude",
    "abs_magnitude":                  "absolute magnitude",

    # estimated diameter (km, min/max)
    "estdiainkmmin":                  "est dia in km(min)",
    "estimatediameterinkmmin":        "est dia in km(min)",
    "mindiameterkm":                  "est dia in km(min)",

    "estdiainkmmax":                  "est dia in km(max)",
    "estimatediameterinkmmax":        "est dia in km(max)",
    "maxdiameterkm":                  "est dia in km(max)",

    # estimated diameter (m, min/max)
    "estdiainmmin":                   "est dia in m(min)",
    "estimatediameterinmmin":         "est dia in m(min)",
    "mindiameterm":                   "est dia in m(min)",

    "estdiainmmax":                   "est dia in m(max)",
    "estimatediameterinmmax":         "est dia in m(max)",
    "maxdiameterm":                   "est dia in m(max)",

    # estimated diameter (miles, min/max)
    "estdiainmilesmin":               "est dia in miles(min)",
    "estimatediameterinmilesmin":     "est dia in miles(min)",
    "mindiametermiles":               "est dia in miles(min)",

    "estdiainmilesmax":               "est dia in miles(max)",
    "estimatediameterinmilesmax":     "est dia in miles(max)",
    "maxdiametermiles":               "est dia in miles(max)",

    # estimated diameter (feet, min/max)
    "estdiainfeetmin":                "est dia in feet(min)",
    "estimatediameterinfeetmin":      "est dia in feet(min)",
    "mindiameterfeet":                "est dia in feet(min)",

    "estdiainfeetmax":                "est dia in feet(max)",
    "estimatediameterinfeetmax":      "est dia in feet(max)",
    "maxdiameterfeet":                "est dia in feet(max)",

    "hazardous":                      "hazardous",
    "hazardousflag":                  "hazardous",
    "ishazardous":                    "hazardous",

    # --- close_approach table ---
    "closeapproach":                  "close_approach",
    "closeapproachdate":              "close approach date",
    "close_approach_date":            "close approach date",
    "approachdate":                   "close approach date",
    "dateofcloseapproach":            "close approach date",

    "epochdatecloseapproach":         "epoch date close approach",
    "epoch_date_close_approach":      "epoch date close approach",

    "relativevelocitykmpersec":       "relative velocity km per sec",
    "velocitykmps":                   "relative velocity km per sec",
    "speedkmps":                      "relative velocity km per sec",

    "relativevelocitykmperhr":        "relative velocity km per hr",
    "velocitykmph":                   "relative velocity km per hr",
    "speedkmph":                      "relative velocity km per hr",

    "milesperhour":                   "miles per hour",
    "mph":                            "miles per hour",

    "missdistastronomical":           "miss dist.(astronomical)",
    "missdistastronomical":           "miss dist.(astronomical)",
    "astronomicalmissdistance":       "miss dist.(astronomical)",

    "missdistlunar":                  "miss dist.(lunar)",
    "lunarmissdistance":              "miss dist.(lunar)",

    "missdistkilometers":             "miss dist.(kilometers)",
    "missdistancekilometers":         "miss dist.(kilometers)",

    "missdistmiles":                  "miss dist.(miles)",
    "missdistancesmiles":             "miss dist.(miles)",

    "orbitingbody":                   "orbiting body",
    "orbiting":                       "orbiting body",

    # --- orbit_data table ---
    "orbitdata":                      "orbit_data",
    "orbitid":                        "orbit id",
    "orbit_id":                       "orbit id",
    "orbitid":                        "orbit id",

    "orbitdeterminationdate":         "orbit determination date",
    "orbit_determination_date":       "orbit determination date",
    "dateoforbitdetermination":       "orbit determination date",

    "orbituncertainity":              "orbit uncertainity",
    "uncertainity":                   "orbit uncertainity",

    "minimumorbitintersection":       "minimum orbit intersection",
    "minorbitintersection":           "minimum orbit intersection",

    "jupitertisserandinvariant":      "jupiter tisserand invariant",
    "tisserandinvariant":             "jupiter tisserand invariant",

    "epochosculation":                "epoch osculation",

    "eccentricity":                   "eccentricity",

    "semimajoraxis":                  "semi major axis",
    "semimajoraxis":                  "semi major axis",

    "inclination":                    "inclination",

    "ascnodelongitude":               "asc node longitude",
    "asc_node_longitude":             "asc node longitude",

    "orbitalperiod":                  "orbital period",
    "orbital_period":                 "orbital period",

    "periheliondistance":             "perihelion distance",
    "perihelionarg":                  "perihelion arg",
    "apheliondist":                   "aphelion dist",
    "periheliontime":                 "perihelion time",

    "meananomaly":                    "mean anomaly",
    "meanmotion":                     "mean motion",

    "equinox":                        "equinox",

    # --- table ---
    "astronaut":                   "astronauts_db",
    "astronauts":                  "astronauts_db",
    "astronautdb":                 "astronauts_db",
    "astronautsdb":                "astronauts_db",
    "crew":                        "astronauts_db",
    "crewdb":                      "astronauts_db",
    "astronautrecord":             "astronauts_db",

    # --- id ---
    "id":                          "id",
    "astronautid":                 "id",
    "crewid":                      "id",

    # --- number ---
    "number":                      "number",
    "astronautnumber":             "number",
    "num":                         "number",
    "no":                          "number",

    # --- nationwide_number ---
    "nationwidenumber":            "nationwide_number",
    "nationwide":                  "nationwide_number",
    "natwidenumber":               "nationwide_number",

    # --- original_name ---
    "originalname":                "original_name",
    "name":                        "original_name",
    "fullname":                    "original_name",
    "astronautname":               "original_name",

    # --- sex ---
    "sex":                         "sex",
    "gender":                      "sex",

    # --- year_of_birth ---
    "yearofbirth":                 "year_of_birth",
    "birthyear":                   "year_of_birth",
    "birth":                       "year_of_birth",
    "born":                        "year_of_birth",

    # --- nationality ---
    "nationality":                 "nationality",
    "citizenship":                 "nationality",
    "country":                     "nationality",

    # --- military_civilian ---
    "militarycivilian":            "military_civilian",
    "status":                      "military_civilian",
    "militaryorcivilian":          "military_civilian",

    # --- selection ---
    "selection":                   "selection",
    "selectionyear":               "selection",
    "astronautselection":          "selection",

    # --- year_of_selection ---
    "yearofselection":             "year_of_selection",
    "selectionyear":               "year_of_selection",

    # --- mission_number ---
    "missionnumber":               "mission_number",
    "missionnum":                  "mission_number",
    "astronautmissionnumber":      "mission_number",

    # --- total_number_of_missions ---
    "totalnumberofmissions":       "total_number_of_missions",
    "totalmissions":               "total_number_of_missions",
    "nummissions":                 "total_number_of_missions",

    # --- occupation ---
    "occupation":                  "occupation",
    "job":                         "occupation",
    "role":                        "occupation",

    # --- year_of_mission ---
    "yearofmission":               "year_of_mission",
    "missionyear":                 "year_of_mission",

    # --- mission_title ---
    "missiontitle":                "mission_title",
    "missionname":                 "mission_title",

    # --- ascend_shuttle ---
    "ascendshuttle":               "ascend_shuttle",
    "launchshuttle":               "ascend_shuttle",
    "ascend":                      "ascend_shuttle",

    # --- in_orbit ---
    "inorbit":                     "in_orbit",
    "orbiting":                    "in_orbit",

    # --- descend_shuttle ---
    "descendshuttle":              "descend_shuttle",
    "landing":                     "descend_shuttle",
    "descend":                     "descend_shuttle",

    # --- hours_mission ---
    "hoursmission":                "hours_mission",
    "missionhours":                "hours_mission",
    "hoursonmission":              "hours_mission",

    # --- total_hrs_sum ---
    "totalhrssum":                 "total_hrs_sum",
    "totalhours":                  "total_hrs_sum",
    "totalhourssum":               "total_hrs_sum",

    # --- field21 ---
    "field21":                     "field21",

    # --- eva_hrs_mission ---
    "evahrsmission":               "eva_hrs_mission",
    "evahours":                    "eva_hrs_mission",
    "evahour":                     "eva_hrs_mission",
    "evamissionhours":             "eva_hrs_mission",

    # --- total_eva_hrs ---
    "totalevahrs":                 "total_eva_hrs",
    "totalevahours":               "total_eva_hrs",
    "totaleva":                    "total_eva_hrs",


    # --- Tables ---
    "neo_reference":                   "neo_reference",
    "neoreference":                    "neo_reference",
    "neo":                             "neo_reference",
    "neo_reference_db":                "neo_reference",

    "close_approach":                  "close_approach",
    "closeapproach":                   "close_approach",
    "close":                           "close_approach",

    "orbit_data":                      "orbit_data",
    "orbitdata":                       "orbit_data",
    "orbit":                           "orbit_data",

    # --- neo_reference columns ---
    "neoreferenceid":                  "Neo Reference ID",
    "neorefid":                        "Neo Reference ID",
    "neo id":                          "Neo Reference ID",

    "name":                            "Name",
    "neo name":                        "Name",

    "absolutemagnitude":               "Absolute Magnitude",
    "absmag":                          "Absolute Magnitude",
    "magnitude":                       "Absolute Magnitude",

    "estdiainkmmin":                   "Est Dia in KM(min)",
    "estimatediameterinkmmin":         "Est Dia in KM(min)",
    "mindiainkm":                      "Est Dia in KM(min)",
    "estdiaminkmmin":                  "Est Dia in KM(min)",

    "estdiainkmmax":                   "Est Dia in KM(max)",
    "maxdiainkm":                      "Est Dia in KM(max)",
    "estdiaminkmmax":                  "Est Dia in KM(max)",

    "estdiainmmin":                    "Est Dia in M(min)",
    "mindiaminm":                      "Est Dia in M(min)",
    "estdiamminm":                     "Est Dia in M(min)",

    "estdiainmmax":                    "Est Dia in M(max)",
    "maxdiainm":                       "Est Dia in M(max)",
    "estdiainmmax":                    "Est Dia in M(max)",

    "estdiainmilesmin":                "Est Dia in Miles(min)",
    "mindiaminmiles":                  "Est Dia in Miles(min)",
    "estdiamilesmin":                  "Est Dia in Miles(min)",

    "estdiainmilesmax":                "Est Dia in Miles(max)",
    "maxdiamiles":                     "Est Dia in Miles(max)",
    "estdiamilesmax":                  "Est Dia in Miles(max)",

    "estdiainfeetmin":                 "Est Dia in Feet(min)",
    "mindiafeet":                      "Est Dia in Feet(min)",
    "estdiafeetmin":                   "Est Dia in Feet(min)",

    "estdiainfeetmax":                 "Est Dia in Feet(max)",
    "maxdiafeet":                      "Est Dia in Feet(max)",
    "estdiafeetmax":                   "Est Dia in Feet(max)",

    # --- close_approach columns ---
    "neoreferenceid":                  "Neo Reference ID",
    "closeapproachdate":               "Close Approach Date",
    "close date":                      "Close Approach Date",
    "approachdate":                    "Close Approach Date",

    "epochdatecloseapproach":          "Epoch Date Close Approach",
    "epochapproach":                   "Epoch Date Close Approach",

    "relativevelocitykmpersec":        "Relative Velocity km per sec",
    "velocitykmps":                    "Relative Velocity km per sec",
    "kmpersec":                        "Relative Velocity km per sec",

    "relativevelocitykmperhr":         "Relative Velocity km per hr",
    "velocitykmph":                    "Relative Velocity km per hr",
    "kmperhr":                         "Relative Velocity km per hr",

    "milesperhour":                    "Miles per hour",
    "mph":                             "Miles per hour",

    "missdistastronomical":            "Miss Dist.(Astronomical)",
    "astronomicalmiss":                "Miss Dist.(Astronomical)",

    "missdistlunar":                   "Miss Dist.(lunar)",
    "lunarmiss":                       "Miss Dist.(lunar)",

    "missdistkilometers":              "Miss Dist.(kilometers)",
    "kmmissdist":                      "Miss Dist.(kilometers)",

    "missdistmiles":                   "Miss Dist.(miles)",
    "milesmiss":                       "Miss Dist.(miles)",

    # --- orbit_data columns ---
    "neoreferenceid":                  "Neo Reference ID",
    "orbitingbody":                    "Orbiting Body",
    "orbitbody":                       "Orbiting Body",

    "orbitid":                         "Orbit ID",
    "orbit id":                        "Orbit ID",

    "orbitdeterminationdate":          "Orbit Determination Date",
    "determinationdate":               "Orbit Determination Date",

    "orbituncertainty":                "Orbit Uncertainity",
    "orbituncertainity":               "Orbit Uncertainity",

    "minimumorbitintersection":        "Minimum Orbit Intersection",
    "minorbitint":                     "Minimum Orbit Intersection",

    "jupitertisserandinvariant":       "Jupiter Tisserand Invariant",
    "tisserandinvariant":              "Jupiter Tisserand Invariant",

    "epochosculation":                 "Epoch Osculation",

    "eccentricity":                    "Eccentricity",

    "semimajoraxis":                   "Semi Major Axis",
    "semimajor":                       "Semi Major Axis",

    "inclination":                     "Inclination",

    "ascnodelongitude":                "Asc Node Longitude",
    "nodelongitude":                   "Asc Node Longitude",

    "orbitalperiod":                   "Orbital Period",
    "period":                          "Orbital Period",

    "periheliondistance":              "Perihelion Distance",
    "perihelionarg":                   "Perihelion Arg",
    "apheliondist":                    "Aphelion Dist",

    "periheliontime":                  "Perihelion Time",

    "meananomaly":                     "Mean Anomaly",
    "meanmotion":                      "Mean Motion",

    "equinox":                         "Equinox",

    "hazardous":                       "Hazardous",
    "hazardflag":                     "Hazardous",

     # --- tables ---
    "personalinfo":           "personal_info",
    "personalinformation":    "personal_info",
    "persinfo":               "personal_info",

    "missioninfo":            "mission_info",
    "missiondata":            "mission_info",

    "missionperformance":     "mission_performance",
    "performance":            "mission_performance",
    "perf":                   "mission_performance",

    # --- personal_info columns ---
    "id":                     "id",
    "astronautid":            "id",
    "crewid":                 "id",

    "number":                 "number",
    "astronautnumber":        "number",

    "nationwidenumber":       "nationwide_number",
    "nationwide":             "nationwide_number",
    "natwidenumber":          "nationwide_number",

    "name":                   "name",
    "fullname":               "name",
    "astronautname":          "name",

    "originalname":           "original_name",
    "origname":               "original_name",

    "sex":                    "sex",
    "gender":                 "sex",

    "yearofbirth":            "year_of_birth",
    "birthyear":              "year_of_birth",
    "born":                   "year_of_birth",

    "nationality":            "nationality",
    "citizenship":            "nationality",
    "country":                "nationality",

    "militarycivilian":       "military_civilian",
    "status":                 "military_civilian",
    "militaryorcivilian":     "military_civilian",

    # --- mission_info columns ---
    "selection":              "selection",
    "selectionyear":          "selection",
    "astronautselection":     "selection",

    "yearofselection":        "year_of_selection",

    "missionnumber":          "mission_number",
    "missionno":              "mission_number",

    "totalnumberofmissions":  "total_number_of_missions",
    "totalmissions":          "total_number_of_missions",

    "occupation":             "occupation",
    "job":                    "occupation",
    "role":                   "occupation",

    "yearofmission":          "year_of_mission",
    "missionyear":            "year_of_mission",

    "missiontitle":           "mission_title",
    "missionname":            "mission_title",
    "title":                  "mission_title",

    # --- mission_performance columns ---
    "ascendshuttle":          "ascend_shuttle",
    "launchshuttle":          "ascend_shuttle",
    "boarding":               "ascend_shuttle",

    "inorbit":                "in_orbit",
    "orbiting":               "in_orbit",

    "descendshuttle":         "descend_shuttle",
    "landing":                "descend_shuttle",
    "return":                 "descend_shuttle",

    "hoursmission":           "hours_mission",
    "missionhours":           "hours_mission",
    "duration":               "hours_mission",

    "totalhrssum":            "total_hrs_sum",
    "totalhours":             "total_hrs_sum",
    "totalhrs":               "total_hrs_sum",

    "field21":                "field21",

    "evahrsmission":          "eva_hrs_mission",
    "evahours":               "eva_hrs_mission",
    "eva":                    "eva_hrs_mission",

    "totalevahrs":            "total_eva_hrs",
    "totalevahours":          "total_eva_hrs",
    "totaleva":               "total_eva_hrs",

      # --- basic_info table ---  
    "satelliteidfake":                    "Satellite ID(Fake)",
    "satelliteidf":                       "Satellite ID(Fake)",
    "satidf":                             "Satellite ID(Fake)",

    "nameofsatellitealternatenames":      "Name of Satellite, Alternate Names",
    "alternatenames":                     "Name of Satellite, Alternate Names",
    "satellitenames":                     "Name of Satellite, Alternate Names",

    "currentofficialnameofsatellite":     "Current Official Name of Satellite",
    "officialname":                       "Current Official Name of Satellite",

    "countryorgofunregistry":             "Country/Org of UN Registry",
    "countryofunregistry":                "Country/Org of UN Registry",
    "unregistrycountry":                  "Country/Org of UN Registry",

    "countryofoperatorowner":             "Country of Operator/Owner",
    "operatorcountry":                    "Country of Operator/Owner",
    "countryowner":                       "Country of Operator/Owner",

    "operatorowner":                      "Operator/Owner",
    "operator":                           "Operator/Owner",
    "owner":                              "Operator/Owner",

    "users":                              "Users",
    "user":                               "Users",

    "purpose":                            "Purpose",
    "detailedpurpose":                    "Detailed Purpose",
    "details":                            "Detailed Purpose",

    # --- orbital_info table ---
    "satelliteidfake":                    "Satellite ID(Fake)",

    "classoforbit":                       "Class of Orbit",
    "orbitclass":                         "Class of Orbit",

    "typeoforbit":                        "Type of Orbit",
    "orbittype":                          "Type of Orbit",

    "longitudeofgeodegrees":              "Longitude of GEO (degrees)",
    "geolongitude":                       "Longitude of GEO (degrees)",
    "longitudegeo":                       "Longitude of GEO (degrees)",

    "perigeekm":                          "Perigee (km)",
    "perigee":                            "Perigee (km)",
    "perigeedistancekm":                  "Perigee (km)",

    "apogeekm":                           "Apogee (km)",
    "apogee":                             "Apogee (km)",
    "apogeedistancekm":                   "Apogee (km)",

    "eccentricity":                       "Eccentricity",
    "inclinationdegrees":                 "Inclination (degrees)",
    "inclination":                        "Inclination (degrees)",

    "periodminutes":                      "Period (minutes)",
    "orbitalperiod":                     "Period (minutes)",
    "period":                             "Period (minutes)",

    # --- launch_info table ---
    "satelliteidfake":                    "Satellite ID(Fake)",
    "launchmasskg":                       "Launch Mass (kg.)",
    "launchmass":                         "Launch Mass (kg.)",

    "drymasskg":                          "Dry Mass (kg.)",
    "drymass":                            "Dry Mass (kg.)",

    "powerwatts":                         "Power (watts)",
    "power":                              "Power (watts)",

    "dateoflaunch":                       "Date of Launch",
    "launchepoch":                        "Date of Launch",
    "launchdate":                         "Date of Launch",

    "expectedlifetimeryrs":               "Expected Lifetime (yrs.)",
    "expectedlifetime":                   "Expected Lifetime (yrs.)",

    "contractor":                         "Contractor",
    "countryofcontractor":                "Country of Contractor",
    "contractorcountry":                  "Country of Contractor",

    "launchsite":                         "Launch Site",
    "site":                               "Launch Site",

    "launchvehicle":                      "Launch Vehicle",
    "vehicle":                            "Launch Vehicle",

    "cosparnumber":                       "COSPAR Number",
    "cosparid":                           "COSPAR Number",

    "noradnumber":                        "NORAD Number",
    "noradid":                            "NORAD Number",

    "comments":                           "Comments",
    "note":                               "Comments",

    # --- tables ---
    "satelliteidentity":       "satellite_identity",
    "identity":                "satellite_identity",
    "satidentity":             "satellite_identity",

    "satellitephysical":       "satellite_physical",
    "physical":                "satellite_physical",
    "satphysical":             "satellite_physical",

    # --- common columns ---
    "planet":                  "planet",
    "planets":                 "planet",
    "world":                   "planet",

    "name":                    "name",
    "satellitename":           "name",
    "bodyname":                "name",

    # --- gm (standard gravitational parameter) ---
    "gm":                      "gm",
    "gravitationalparameter":  "gm",
    "standardgravparameter":   "gm",
    "gravparam":               "gm",

    # --- radius ---
    "radius":                  "radius",
    "meanradius":              "radius",
    "equatorialradius":        "radius",
    "polarradius":             "radius",
    "rad":                     "radius",

    # --- density ---
    "density":                 "density",
    "massdensity":             "density",
    "averagedensity":          "density",

    # --- magnitude ---
    "magnitude":               "magnitude",
    "mag":                     "magnitude",
    "visualmagnitude":         "magnitude",

    # --- albedo ---
    "albedo":                  "albedo",
    "reflectivity":            "albedo",
    "surfacealbedo":           "albedo",
    "geometricalbedo":         "albedo",

     # --- tables ---
    "rockergeneralinfo":        "rocket_general_info",
    "rocket_general_info":      "rocket_general_info",
    "generalinfo":              "rocket_general_info",
    "rocketgeneral":            "rocket_general_info",

    "rockettechnicalspecs":     "rocket_technical_specs",
    "rocket_technical_specs":   "rocket_technical_specs",
    "technicalspecs":           "rocket_technical_specs",
    "rockettechspecs":          "rocket_technical_specs",

    # --- rocket_general_info columns ---
    "name":                     "Name",
    "rocketname":               "Name",

    "cmp":                      "Cmp",
    "company":                  "Cmp",

    "wiki":                     "Wiki",
    "wikipedia":                "Wiki",
    "wikilink":                 "Wiki",

    "status":                   "Status",
    "rocketstatus":             "Status",
    "state":                    "Status",

    # --- rocket_technical_specs columns ---
    "liftoffthrust":            "Liftoff_Thrust",
    "liftoff":                  "Liftoff_Thrust",
    "launchthrust":             "Liftoff_Thrust",
    "thrust":                   "Liftoff_Thrust",

    "payloadleo":               "Payload_LEO",
    "payloadtoleo":             "Payload_LEO",
    "leopayload":               "Payload_LEO",
    "leo":                      "Payload_LEO",

    "stages":                   "Stages",
    "stage":                    "Stages",

    "strapons":                 "Strap_ons",
    "strapons":                 "Strap_ons",
    "strap-ons":                "Strap_ons",
    "strapon":                  "Strap_ons",

    "rocketheightm":            "Rocket_Height_m",
    "rocketheight":             "Rocket_Height_m",
    "heightm":                  "Rocket_Height_m",

    "pricemusd":                "Price_MUSD",
    "priceusd":                 "Price_MUSD",
    "price":                    "Price_MUSD",
    "cost":                     "Price_MUSD",

    "payloadgto":               "Payload_GTO",
    "gtopayload":               "Payload_GTO",
    "gto":                      "Payload_GTO",

    "fairingdiameterm":         "Fairing_Diameter_m",
    "fairingdiameter":          "Fairing_Diameter_m",
    "diameterfairingm":         "Fairing_Diameter_m",

    "fairingheightm":           "Fairing_Height_m",
    "fairingheight":            "Fairing_Height_m",
    "heightfairingm":           "Fairing_Height_m",

    # --- tables ---
    "newsarticlestable":    "news_articles_table",
    "newsarticles":         "news_articles_table",
    "newsarticle":          "news_articles_table",
    "news":                 "news_articles_table",
    "articles":             "news_articles_table",
    "articlestable":        "news_articles_table",
    "news_table":           "news_articles_table",

    "publishinginfo":       "publishing_info",
    "publishing":           "publishing_info",
    "pubinfo":              "publishing_info",
    "pub":                  "publishing_info",
    "publishinfo":          "publishing_info",

    # --- news_articles_table columns ---
    "title":                "title",
    "headline":             "title",
    "heading":              "title",
    "articletitle":         "title",

    "url":                  "url",
    "link":                 "url",
    "weblink":              "url",
    "articleurl":           "url",

    "content":              "content",
    "body":                 "content",
    "articlecontent":       "content",
    "text":                 "content",

    "postexcerpt":          "postexcerpt",
    "excerpt":              "postexcerpt",
    "summary":              "postexcerpt",
    "teaser":               "postexcerpt",

    # --- publishing_info columns ---
    "author":               "author",
    "writer":               "author",
    "journalist":           "author",
    "postedby":             "author",

    "date":                 "date",
    "publishdate":          "date",
    "publicationdate":      "date",
    "postdate":             "date",
    "pdate":                "date",

     # --- table “stars” ---
    "star":            "stars",
    "stars":           "stars",
    "stardb":          "stars",
    "starsdb":         "stars",
    "starstable":      "stars",

    # --- column “star name” ---
    "starname":        "star name",
    "starnames":       "star name",

    # --- column “distance” ---
    "distance":        "distance",
    "dist":            "distance",
    "range":           "distance",

    # --- column “mass” ---
    "mass":            "mass",

    # --- column “radius” ---
    "radius":          "radius",
    "rad":             "radius",

    # --- column “luminosity” ---
    "luminosity":      "luminosity",
    "lumin":           "luminosity",
    "bright":          "luminosity",
    "brightness":      "luminosity",

     # --- tables ---
    # organizations table
    "organizations":         "organizations",
    "organisationstable":    "organizations",
    "organizationstable":    "organizations",
    "orgs":                  "organizations",
    "orgstable":             "organizations",

    # rockets table
    "rockets":               "rockets",
    "rocketstable":          "rockets",
    "rocketstable":          "rockets",

    # missions table
    "missions":              "missions",
    "missionstable":         "missions",
    "missionstable":         "missions",

    # --- organizations columns ---
    "organisation":          "organisation",
    "organization":          "organisation",
    "org":                   "organisation",

    "location":              "location",
    "loc":                   "location",
    "site":                  "location",
    "place":                 "location",

    # --- rockets columns ---
    "organisation":          "organisation",
    "organization":          "organisation",
    "org":                   "organisation",

    "details":               "details",
    "detail":                "details",
    "description":           "details",
    "desc":                  "details",

    "rocketstatus":          "rocket_status",
    "rocket_state":          "rocket_status",
    "status":                "rocket_status",
    "state":                 "rocket_status",

    "price":                 "price",
    "cost":                  "price",
    "budget":                "price",

    # --- missions columns ---
    "organisation":          "organisation",
    "organization":          "organisation",
    "org":                   "organisation",

    "missionstatus":         "mission_status",
    "mission_state":         "mission_status",
    "status":                "mission_status",
    "state":                 "mission_status",
    "missionstate":          "mission_status",
}


    matched_entities = []

    normalized_schema = {term.lower().replace("_", ""): term for term in schema_terms}

    for token in tokens:
        base = token.lower().replace("_", "")
        if base in normalized_schema:
            original = normalized_schema[base]
            matched_entities.append({
                'type': 'table' if original.endswith('_db') else 'column',
                'value': original
            })
        elif token in synonym_map:
            mapped = synonym_map[token]
            if mapped in schema_terms:
                matched_entities.append({
                    'type': 'table' if mapped.endswith('_db') else 'column',
                    'value': mapped
                })

    return matched_entities

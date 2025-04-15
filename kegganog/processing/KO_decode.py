#!/usr/bin/python

# THIS FUNCTION IS STILL AT WORK. SOMEDAY I WILL FINISH IT AND IT WILL REPLACE KEGG-DECODER.
# THE MAIN PURPOSE OF THIS SCRIPT IS TO BE MODERN AND EASY TO UNDERSTAND.
# I WANT ANY USER TO EASILY UNDERSTAND THIS SCRIPT, SO, THEY CAN MAKE CHANGES AND UPDATES TO THIS SCRIPT.
# BUT NOW THE SCRIPT IS NOT YET READY. IT IS BUGGY! I MUST DEBUG IT BEFORE THE RELEASE!

import argparse
import matplotlib


def nitrogen(ko_match):
    """
    Calculate the presence of nitrogen-related processes based on KO identifiers.

    Args:
        ko_match (list): List of KO identifiers to match against nitrogen-related processes.

    Returns:
        dict: A dictionary with nitrogen-related processes as keys and their presence (0 or 1) as values.
              For some processes, fractional presence (e.g., 0.33) may be indicated.
    """

    def check_presence(kos, threshold=1):
        """
        Check if a process is present based on required KO identifiers.

        Args:
            kos (list): List of required KO identifiers for the process.
            threshold (float): Minimum number of matching KOs required to mark the process as present.

        Returns:
            float: 1 if all required KOs are present, fractional if partially matched.
        """
        matched_count = sum(1 for ko in kos if ko in ko_match)
        return matched_count / len(kos) if matched_count >= threshold else 0

    # Initialize the output dictionary with default values.
    processes = {
        "dissim nitrate reduction": 0,
        "nitrite oxidation": 0,
        "DNRA": 0,
        "nitrite reduction": 0,
        "nitric oxide reduction": 0,
        "nitrous-oxide reduction": 0,
        "nitrogen fixation": 0,
        "hydroxylamine oxidation": 0,
        "ammonia oxidation (amo/pmmo)": 0,
        "hydrazine dehydrogenase": 0,
        "hydrazine synthase": 0,
    }

    # Define KO identifier groups for each process.
    ko_groups = {
        "dissim nitrate reduction": [["K00370", "K00371"], ["K02567", "K02568"]],
        "nitrite oxidation": [["K00370", "K00371"]],
        "DNRA": [["K00362", "K00363"], ["K03385", "K15876"]],
        "nitrite reduction": [["K00368"], ["K15864"]],
        "nitric oxide reduction": [["K04561", "K02305"]],
        "nitrous-oxide reduction": [["K00376"]],
        "nitrogen fixation": [["K02586"], ["K02591"], ["K02588"]],
        "hydroxylamine oxidation": [["K10535"]],
        "ammonia oxidation (amo/pmmo)": [["K10944"], ["K10945"], ["K10946"]],
        "hydrazine dehydrogenase": [["K20935"]],
        "hydrazine synthase": [["K20932"], ["K20933"], ["K20934"]],
    }

    # Evaluate each process.
    for process, groups in ko_groups.items():
        if (
            process == "nitrogen fixation"
            or process == "ammonia oxidation (amo/pmmo)"
            or process == "hydrazine synthase"
        ):
            # Special handling for processes with partial contributions.
            processes[process] = sum(check_presence(group) for group in groups)
        else:
            # Standard evaluation for processes requiring all groups to be present.
            processes[process] = max(check_presence(group) for group in groups)

    return processes


def glycolysis(ko_match):
    """
    Calculate the completeness of glycolysis pathway based on KO identifiers.

    Args:
        ko_match (list): List of KO identifiers to match against glycolysis pathway genes.

    Returns:
        dict: A dictionary with a single key 'glycolysis' and a value representing
              the fraction of glycolysis pathway genes present (scaled from 0 to 1, rounded to two decimals).
    """

    def check_presence(kos):
        """
        Check if any KO in a group is present in the input KO identifiers.

        Args:
            kos (list): List of KO identifiers for a specific enzyme or group.

        Returns:
            int: 1 if any KO from the group is present, 0 otherwise.
        """
        return 1 if any(ko in ko_match for ko in kos) else 0

    # Define KO groups for each step in glycolysis.
    ko_groups = {
        # Single KO enzymes
        "phosphoglucomutase": ["K01835"],
        "glucose-6-phosphate isomerase": ["K01810"],
        "fructose-bisphosphate aldolase": ["K01623"],
        "phosphoglycerate kinase": ["K00927"],
        "enolase": ["K01689"],
        # Multiple KO options for the same function
        "6-phosphofructokinase": ["K00850", "K00895"],
        "glyceraldehyde 3-phosphate dehydrogenase": ["K00134", "K00150"],
        "2,3-bisphosphoglycerate-dependent phosphoglycerate mutase": [
            "K01834",
            "K15633",
        ],
        "pyruvate kinase": ["K00873", "K01006"],
    }

    # Calculate the total number of glycolysis-related KOs present.
    total = sum(check_presence(kos) for kos in ko_groups.values())

    # Calculate the completeness of glycolysis as a fraction of total genes (9 in total).
    glycolysis_fraction = total / len(ko_groups)

    # Return the result rounded to two decimals.
    return {"glycolysis": round(glycolysis_fraction, 2)}


def gluconeogenesis(ko_match):
    """
    Calculate the completeness of the gluconeogenesis pathway based on KO identifiers.

    Args:
        ko_match (list): List of KO identifiers to match against gluconeogenesis pathway genes.

    Returns:
        dict: A dictionary with a single key 'gluconeogenesis' and a value representing
              the fraction of gluconeogenesis pathway genes present (scaled from 0 to 1, rounded to two decimals).
    """

    def check_presence(kos):
        """
        Check if any KO in a group is present in the input KO identifiers.

        Args:
            kos (list): List of KO identifiers for a specific enzyme or group.

        Returns:
            int: 1 if any KO from the group is present, 0 otherwise.
        """
        return 1 if any(ko in ko_match for ko in kos) else 0

    # Define KO groups for each step in gluconeogenesis.
    ko_groups = {
        # Mandatory for gluconeogenesis to proceed
        "fructose-1,6-bisphosphatase": ["K03841"],
        # Single KO enzymes
        "phosphoglucomutase": ["K01835"],
        "glucose-6-phosphate isomerase": ["K01810"],
        "fructose-bisphosphate aldolase": ["K01623"],
        "phosphoglycerate kinase": ["K00927"],
        "enolase": ["K01689"],
        # Multiple KO options for the same function
        "glyceraldehyde 3-phosphate dehydrogenase": ["K00134", "K00150"],
        "2,3-bisphosphoglycerate-dependent phosphoglycerate mutase": [
            "K01834",
            "K15633",
        ],
        "pyruvate kinase": ["K00873", "K01006"],
    }

    # Check if the mandatory enzyme (fructose-1,6-bisphosphatase) is present.
    if not check_presence(ko_groups["fructose-1,6-bisphosphatase"]):
        return {"gluconeogenesis": 0.0}

    # Calculate the total number of gluconeogenesis-related KOs present.
    total = sum(check_presence(kos) for key, kos in ko_groups.items())

    # Calculate the completeness of gluconeogenesis as a fraction of total genes (9 in total).
    gluconeogenesis_fraction = total / len(ko_groups)

    # Return the result rounded to two decimals.
    return {"gluconeogenesis": round(gluconeogenesis_fraction, 2)}


def tca_cycle(ko_match):
    """
    Calculate the completeness of the TCA cycle based on KO identifiers.

    Args:
        ko_match (list): List of KO identifiers to match against TCA cycle genes.

    Returns:
        dict: A dictionary with a single key 'TCA Cycle' and a value representing
              the fraction of TCA cycle genes present (scaled from 0 to 1, rounded to two decimals).
    """

    def check_presence(kos, all_required=False):
        """
        Check if any or all KOs in a group are present in the input KO identifiers.

        Args:
            kos (list): List of KO identifiers for a specific enzyme or group.
            all_required (bool): If True, requires all KOs to be present; if False, any KO suffices.

        Returns:
            int: 1 if the required KOs are present, 0 otherwise.
        """
        if all_required:
            return 1 if all(ko in ko_match for ko in kos) else 0
        else:
            return 1 if any(ko in ko_match for ko in kos) else 0

    # Define KO groups for each step in the TCA cycle.
    ko_groups = {
        "aconitate hydratase": [["K01681", "K01682"]],
        "isocitrate dehydrogenase": [["K00031"], ["K00030"], ["K17753"]],
        "2-oxoglutarate/2-oxoacid ferredoxin oxidoreductase": [["K00174", "K00175"]],
        "succinyl-CoA synthetase": [
            ["K01899", "K01900"],
            ["K01902", "K01903"],
            ["K18118"],
        ],
        "fumarate reductase": [
            ["K00244", "K00245", "K00246", "K00247"],
            ["K00239", "K00240", "K00241", "K00242"],
            ["K00234", "K00235", "K00236", "K00237"],
        ],
        "fumarate hydratase": [["K01677", "K01678", "K01679"], ["K01676"]],
        "malate dehydrogenase": [["K00116"], ["K00025"], ["K00026"], ["K00024"]],
        "citrate synthase": [["K01647"]],
    }

    # Calculate the total number of TCA cycle-related KOs present.
    total = 0
    for enzyme, groups in ko_groups.items():
        # Some enzymes require all KOs in a group to be present, others require any KO.
        for group in groups:
            total += check_presence(group, all_required=len(group) > 1)

    # Calculate the completeness of the TCA cycle as a fraction of total steps (8 in total).
    tca_cycle_fraction = total / len(ko_groups)

    # Return the result rounded to two decimals.
    return {"TCA Cycle": round(tca_cycle_fraction, 2)}


def cbb_cycle(ko_match):
    """
    Calculate the completeness of the Calvin-Benson-Bassham (CBB) cycle based on KO identifiers.

    Args:
        ko_match (list): List of KO identifiers to match against CBB cycle genes.

    Returns:
        dict: A dictionary containing:
            - 'RuBisCo': Indicates the presence (1) or absence (0) of RuBisCO (large subunit Type 1 or 2).
            - 'CBB Cycle': Fraction of CBB cycle completeness (scaled from 0 to 1, rounded to two decimals).
    """

    def check_presence(kos, all_required=False):
        """
        Check if any or all KOs in a group are present in the input KO identifiers.

        Args:
            kos (list): List of KO identifiers for a specific enzyme or group.
            all_required (bool): If True, requires all KOs to be present; if False, any KO suffices.

        Returns:
            int: 1 if the required KOs are present, 0 otherwise.
        """
        if all_required:
            return 1 if all(ko in ko_match for ko in kos) else 0
        else:
            return 1 if any(ko in ko_match for ko in kos) else 0

    # Initialize the output data and count variables.
    out_data = {"RuBisCo": 0, "CBB Cycle": 0}
    total = 0
    var_count = 4  # Start with the base number of steps in the cycle.

    # Check for RuBisCO (large subunit Type 1 or 2).
    if check_presence(["K01601"]):
        out_data["RuBisCo"] = 1
        total += 1

        # Define the KO groups for other enzymes in the CBB cycle.
        enzyme_groups = {
            "phosphoglycerate kinase": ["K00927"],
            "glyceraldehyde 3-phosphate dehydrogenase": ["K00134", "K05298", "K00150"],
            "phosphoribulokinase": ["K00855"],
            # Ribulose regeneration (multiple configurations)
            "ribulose-phosphate 3-epimerase AND xylulose-5-phosphate/fructose-6-phosphate phosphoketolase": {
                "kos": ["K01783", "K01621"],
                "value": 2,
            },
            "transketolase AND ribulose-phosphate 3-epimerase": {
                "kos": ["K00615", "K01783"],
                "value": 2,
            },
            "transketolase AND ribose 5-phosphate isomerase": {
                "kos": ["K00615", "K01807"],
                "value": 2,
            },
            "fructose-bisphosphate aldolase AND transketolase AND fructose-1,6-bisphosphatase": {
                "kos": [
                    ["K01623", "K01624", "K11645"],  # fructose-bisphosphate aldolase
                    ["K00615"],  # transketolase
                    ["K11532", "K03841", "K02446"],  # fructose-1,6-bisphosphatase
                ],
                "value": 3,
            },
        }

        # Evaluate the presence of enzymes in the cycle.
        for enzyme, data in enzyme_groups.items():
            if isinstance(data, list):  # Single enzyme KO groups
                if check_presence(data):
                    total += 1
            elif isinstance(data, dict):  # Multi-step configurations
                if all(check_presence(kos) for kos in data["kos"]):
                    total += data["value"]
                    var_count += data["value"]

    # Calculate the completeness of the CBB cycle.
    cbb_cycle_fraction = total / var_count
    out_data["CBB Cycle"] = round(cbb_cycle_fraction, 2)

    return out_data


def reverse_tca(ko_match):
    """
    Calculate the presence of the reverse TCA cycle based on KO identifiers.

    Args:
        ko_match (list): List of KO identifiers to match against reverse TCA cycle genes.

    Returns:
        dict: A dictionary containing:
            - 'rTCA Cycle': Presence of the reverse TCA cycle (1 if present, 0 if absent).
    """

    # Define KO groups for reverse TCA cycle.
    ko_groups = {
        # ATP-citrate lyase (both subunits required)
        "ATP-citrate lyase": ["K15230", "K15231"],
        # citryl-CoA synthetase and citryl-CoA lyase (all required KOs)
        "citryl-CoA synthetase and citryl-CoA lyase": ["K15232", "K15233", "K15234"],
    }

    # Initialize output data
    out_data = {"rTCA Cycle": 0}

    # Iterate through each pathway and check for the corresponding KOs
    for pathway, kos in ko_groups.items():
        if all(ko in ko_match for ko in kos):
            out_data["rTCA Cycle"] = 1
            break  # If any pathway is found, stop further checks

    return out_data


def wood_ljungdahl(ko_match):
    """
    Calculate the presence of the Wood-Ljungdahl pathway based on KO identifiers.

    Args:
        ko_match (list): List of KO identifiers to match against Wood-Ljungdahl pathway genes.

    Returns:
        dict: A dictionary containing:
            - 'Wood-Ljungdahl': Presence of the Wood-Ljungdahl pathway (float value).
    """

    # Define KO groups for Wood-Ljungdahl pathway.
    ko_groups = {
        # Carbon fixing branch
        "acetyl-CoA decarbonylase/synthase complex or CO-methylating acetyl-CoA synthase": [
            "K00192",
            "K14138",
        ],
        "CO dehydrogenase catalytic subunits": ["K00198", "K03520"],
        # Methyl branch (only if CO methyl group is present)
        "formate dehydrogenase": ["K05299", "K15022"],
        "formate--tetrahydrofolate ligase": ["K01938"],
        "methylenetetrahydrofolate dehydrogenase (NADP+) / methenyltetrahydrofolate cyclohydrolase": [
            "K01491"
        ],
        "methylenetetrahydrofolate reductase (NADPH)": ["K00297"],
    }

    total = 0
    CO_methyl_present = 0

    # Check if Carbon fixing branch is present.
    if any(
        ko in ko_match
        for ko in ko_groups[
            "acetyl-CoA decarbonylase/synthase complex or CO-methylating acetyl-CoA synthase"
        ]
    ):
        total += 1
        CO_methyl_present = 1  # If this branch is present, CO-methylation is activated.

    # Check for CO dehydrogenase catalytic subunits (must be present).
    if any(ko in ko_match for ko in ko_groups["CO dehydrogenase catalytic subunits"]):
        total += 1

    # If CO methylation is present, check the Methyl branch enzymes.
    if CO_methyl_present == 1:
        for pathway, kos in ko_groups.items():
            if (
                pathway
                != "acetyl-CoA decarbonylase/synthase complex or CO-methylating acetyl-CoA synthase"
                and pathway != "CO dehydrogenase catalytic subunits"
            ):
                if all(ko in ko_match for ko in kos):
                    total += 1

    # Calculate the presence of the pathway as a fraction of the total possible KO checks.
    value = float(total) / float(6)
    return {"Wood-Ljungdahl": float(f"{value:.2f}")}


def three_prop(ko_match):
    """
    Calculates the completion percentage of the 3-Hydroxypropionate Bicycle pathway
    based on the presence of specific KEGG Orthology (KO) groups in the input list.

    Args:
        ko_match (list): A list of KEGG Orthology (KO) identifiers.

    Returns:
        dict: A dictionary containing the pathway name and its completion percentage.
    """

    # Define KO groups for the 3-Hydroxypropionate Bicycle pathway
    ko_groups = {
        # Pyruvate ferredoxin oxidoreductase alpha and beta subunits
        "pyruvate_ferredoxin_oxidoreductase": ["K00169", "K00170"],
        # Pyruvate dikinase
        "pyruvate_dikinase": ["K01006", "K01007"],
        # Phosphoenolpyruvate carboxylase
        "phosphoenolpyruvate_carboxylase": ["K01595"],
        # Malate dehydrogenase
        "malate_dehydrogenase": ["K00024"],
        # Succinyl-CoA:(S)-malate CoA-transferase
        "succinyl_CoA_malate_CoA_transferase": ["K14471", "K14472"],
        # Malyl-CoA/(S)-citramalyl-CoA lyase
        "malyl_CoA_lyase": ["K08691"],
        # Acetyl-CoA carboxylase, biotin carboxylase
        "acetyl_CoA_carboxylase": ["K02160", "K01961", "K01962", "K01963"],
        # Malonyl-CoA reductase / 3-hydroxypropionate dehydrogenase (NADP+)
        "malonyl_CoA_reductase": ["K14468", "K15017"],
        # 3-Hydroxypropionate dehydrogenase (NADP+)
        "hydroxypropionate_dehydrogenase": ["K15039"],
        # Acrylyl-CoA reductase (NADPH) / 3-hydroxypropionyl-CoA dehydratase / 3-hydroxypropionyl-CoA synthetase
        "acrylyl_CoA_reductase": ["K14469", "K15018"],
        # 3-Hydroxypropionyl-coenzyme A dehydratase
        "hydroxypropionyl_CoA_dehydratase": ["K15019"],
        # Acryloyl-coenzyme A reductase
        "acryloyl_CoA_reductase": ["K15020"],
        # 2-Methylfumaryl-CoA hydratase
        "methylfumaryl_CoA_hydratase": ["K14449"],
        # 2-Methylfumaryl-CoA isomerase
        "methylfumaryl_CoA_isomerase": ["K14470"],
        # 3-Methylfumaryl-CoA hydratase
        "methylfumaryl_CoA_hydratase_3": ["K09709"],
    }

    # Calculate the total score based on KO group matches
    total = 0
    for group, ko_list in ko_groups.items():
        if all(ko in ko_match for ko in ko_list):
            total += 1

    # Calculate completion percentage
    value = float(total) / float(len(ko_groups))

    # Return the pathway name and completion percentage
    return {"3-Hydroxypropionate Bicycle": round(value, 2)}


def four_hydrox(ko_match):
    """
    Calculates the completion percentage of the 4-Hydroxybutyrate/3-Hydroxypropionate pathway
    based on the presence of specific KEGG Orthology (KO) groups in the input list.

    Args:
        ko_match (list): A list of KEGG Orthology (KO) identifiers.

    Returns:
        dict: A dictionary containing the pathway name and its completion percentage.
    """

    # Define KO groups for the 4-Hydroxybutyrate/3-Hydroxypropionate pathway
    ko_groups = {
        # Acetyl-CoA carboxylase, biotin carboxylase
        "acetyl_CoA_carboxylase": ["K02160", "K01961", "K01962", "K01963"],
        # Malonic semialdehyde reductase
        "malonic_semialdehyde_reductase": ["K18602"],
        # 3-Hydroxypropionyl-CoA synthetase
        "hydroxypropionyl_CoA_synthetase": ["K18594"],
        # Acrylyl-CoA reductase (NADPH) / 3-Hydroxypropionyl-CoA dehydratase / 3-Hydroxypropionyl-CoA synthetase
        "acrylyl_CoA_reductase": ["K14469", "K15019"],
        # Methylmalonyl-CoA/ethylmalonyl-CoA epimerase
        "methylmalonyl_epimerase": ["K05606"],
        # Methylmalonyl-CoA mutase
        "methylmalonyl_CoA_mutase": ["K01847", "K01848", "K01849"],
        # 4-Hydroxybutyryl-CoA synthetase (ADP-forming)
        "hydroxybutyryl_CoA_synthetase": ["K18593"],
        # 4-Hydroxybutyryl-CoA dehydratase / vinylacetyl-CoA-Delta-isomerase
        "hydroxybutyryl_CoA_dehydratase": ["K14534"],
        # Enoyl-CoA hydratase / 3-Hydroxyacyl-CoA dehydrogenase
        "enoyl_CoA_hydratase": ["K15016"],
        # Acetyl-CoA C-acetyltransferase
        "acetyl_CoA_C_acetyltransferase": ["K00626"],
    }

    # Calculate the total score based on KO group matches
    total = 0
    for group, ko_list in ko_groups.items():
        if all(ko in ko_match for ko in ko_list):
            total += 1

    # Calculate completion percentage
    value = float(total) / float(len(ko_groups))

    # Return the pathway name and completion percentage
    return {"4-Hydroxybutyrate/3-hydroxypropionate": round(value, 2)}


def c_degradation(ko_match):
    """
    Identifies the presence of enzymes involved in carbohydrate degradation based on KEGG Orthology (KO) identifiers.

    Args:
        ko_match (list): A list of KEGG Orthology (KO) identifiers.

    Returns:
        dict: A dictionary with enzyme names as keys and binary values (0 or 1) indicating their presence.
    """

    # Define enzyme groups with associated KO identifiers
    ko_groups = {
        "beta-glucosidase": ["K05350", "K05349"],
        "cellulase": ["K01225", "K19668"],
        "chitinase": ["K01183"],
        "bifunctional chitinase/lysozyme": ["K13381"],
        "basic endochitinase B": ["K20547"],
        "diacetylchitobiose deacetylase": ["K03478", "K18454"],
        "beta-N-acetylhexosaminidase": ["K01207"],
        "pectinesterase": ["K01730"],
        "exo-poly-alpha-galacturonosidase": ["K01184"],
        "oligogalacturonide lyase": ["K01730"],
        "exopolygalacturonase": ["K01184"],
        "D-galacturonate isomerase": ["K01812"],
        "D-galacturonate epimerase": ["K08679"],
        "alpha-amylase": ["K01176"],
        "glucoamylase": ["K01178"],
        "pullulanase": ["K01200"],
    }

    # Initialize the output dictionary with enzyme names set to 0
    out_data = {enzyme: 0 for enzyme in ko_groups}

    # Check for the presence of KO identifiers in the input list
    for enzyme, ko_list in ko_groups.items():
        if any(ko in ko_match for ko in ko_list):
            out_data[enzyme] = 1

    return out_data


def chemotaxis(ko_match):
    """
    Calculates the completeness of the chemotaxis pathway based on KEGG Orthology (KO) identifiers.

    Args:
        ko_match (list): A list of KEGG Orthology (KO) identifiers.

    Returns:
        dict: A dictionary with the pathway name as the key and a float value (0.00 to 1.00) indicating completeness.
    """

    # Define the KO identifiers for the Che family of proteins
    che_proteins = [
        "K13924",  # CheW
        "K00575",  # CheA
        "K03413",  # CheB
        "K03412",  # CheR
        "K03406",  # CheY
        "K03407",  # CheZ
        "K03415",  # CheC
        "K03408",  # CheD
    ]

    # Calculate the number of identified KOs in the input list
    total_present = sum(1 for ko in che_proteins if ko in ko_match)

    # Calculate the completeness as a proportion
    completeness = total_present / len(che_proteins)

    # Return the completeness score rounded to two decimal places
    return {"Chemotaxis": round(completeness, 2)}


def flagellum(ko_match):
    """
    Calculates the completeness of the flagellum biosynthesis pathway based on KEGG Orthology (KO) identifiers.

    Args:
        ko_match (list): A list of KEGG Orthology (KO) identifiers.

    Returns:
        dict: A dictionary with the pathway name as the key and a float value (0.00 to 1.00) indicating completeness.
    """

    # Define the KO identifiers for flagellum biosynthesis components
    flagellum_kos = [
        "K02409",  # FliA
        "K02401",  # FliC
        "K02394",  # FlgE
        "K02397",  # FlgK
        "K02396",  # FlgL
        "K02391",  # FlgB
        "K02390",  # FlgC
        "K02393",  # FlgD
        "K02392",  # FlgF
        "K02386",  # FlhB
        "K02557",  # FlhA
        "K02556",  # FlhF
        "K02400",  # FliD
        "K02418",  # FliH
        "K02389",  # FlgA
        "K02412",  # FliI
        "K02387",  # FlhE
        "K02410",  # FliM
        "K02411",  # FliN
        "K02416",  # FliP
        "K02417",  # FliQ
        "K02407",  # FliR
        "K02406",  # FliS
    ]

    # Calculate the number of identified KOs in the input list
    total_present = sum(1 for ko in flagellum_kos if ko in ko_match)

    # Calculate the completeness as a proportion
    completeness = total_present / len(flagellum_kos)

    # Return the completeness score rounded to two decimal places
    return {"Flagellum": round(completeness, 2)}


def sulfur(ko_match):
    """
    Computes the completeness of various sulfur-related metabolic pathways based on KEGG Orthology (KO) identifiers.

    Args:
        ko_match (list): A list of KEGG Orthology (KO) identifiers.

    Returns:
        dict: A dictionary where keys represent pathway/process names and values indicate their completeness (0.00 to 1.00).
    """

    # Initialize the output dictionary with sulfur-related pathways
    out_data = {
        "sulfur assimilation": 0,
        "dissimilatory sulfate < > APS": 0,
        "dissimilatory sulfite < > APS": 0,
        "dissimilatory sulfite < > sulfide": 0,
        "thiosulfate oxidation": 0,
        "alt thiosulfate oxidation doxAD": 0,
        "alt thiosulfate oxidation tsdA": 0,
        "thiosulfate disproportionation": 0,
        "sulfur reductase sreABC": 0,
        "thiosulfate/polysulfide reductase": 0,
        "sulfhydrogenase": 0,
        "sulfur disproportionation": 0,
        "sulfur dioxygenase": 0,
        "sulfite dehydrogenase": 0,
        "sulfide oxidation": 0,
        "sulfite dehydrogenase (quinone)": 0,
        "DMSP demethylation": 0,
        "DMS dehydrogenase": 0,
        "DMSO reductase": 0,
    }

    # Define pathway-specific KO groups
    pathway_kos = {
        "sulfur assimilation": [["K00392"], ["K00380", "K00381"]],
        "dissimilatory sulfate < > APS": [["K00958"]],
        "dissimilatory sulfite < > APS": [["K00395", "K00394"]],
        "dissimilatory sulfite < > sulfide": [["K11180", "K11181"]],
        "thiosulfate oxidation": [
            ["K17222"],
            ["K17224"],
            ["K17225"],
            ["K17223"],
            ["K17226"],
            ["K17227"],
        ],
        "alt thiosulfate oxidation doxAD": [["K16936", "K16937"]],
        "alt thiosulfate oxidation tsdA": [["K19713"]],
        "sulfur reductase sreABC": [["K17219"], ["K17220"], ["K17221"]],
        "thiosulfate/polysulfide reductase": [["K08352"], ["K08353"], ["K08354"]],
        "sulfhydrogenase": [["K17993"], ["K17996"], ["K17995"], ["K17994"]],
        "sulfur disproportionation": [["K16952"]],
        "sulfur dioxygenase": [["K17725"]],
        "sulfite dehydrogenase": [["K05301"]],
        "sulfide oxidation": [["K17218"], ["K17229"]],
        "sulfite dehydrogenase (quinone)": [["K21307"], ["K21308"], ["K21309"]],
        "DMSP demethylation": [["K17486"]],
        "DMS dehydrogenase": [["K16964"], ["K16965"], ["K16966"]],
        "DMSO reductase": [["K07306"], ["K07307"], ["K07308"]],
    }

    # Evaluate each pathway
    for pathway, ko_groups in pathway_kos.items():
        for group in ko_groups:
            if all(ko in ko_match for ko in group):
                out_data[pathway] += round(1 / len(ko_groups), 2)

    # Adjust "thiosulfate oxidation" to 2 decimal places
    out_data["thiosulfate oxidation"] = round(out_data["thiosulfate oxidation"], 2)

    return out_data


def methanogenesis(ko_match):
    """
    Computes the completeness of methanogenesis pathways based on KEGG Orthology (KO) identifiers.

    Args:
        ko_match (list): A list of KEGG Orthology (KO) identifiers.

    Returns:
        dict: A dictionary where keys represent methanogenesis pathways and values indicate their completeness (0.00 to 1.00).
    """

    # Initialize the output dictionary with methanogenesis pathways
    out_data = {
        "Methanogenesis via methanol": 0,
        "Methanogenesis via dimethylamine": 0,
        "Methanogenesis via dimethylsulfide, methanethiol, methylpropanoate": 0,
        "Methanogenesis via methylamine": 0,
        "Methanogenesis via trimethylamine": 0,
        "Methanogenesis via acetate": 0,
        "Methanogenesis via CO2": 0,
        "Coenzyme M reduction to methane": 0,
        "Coenzyme B/Coenzyme M regeneration": 0,
        "dimethylamine/trimethylamine dehydrogenase": 0,
    }

    # Define pathway-specific KO groups
    pathway_kos = {
        "dimethylamine/trimethylamine dehydrogenase": [["K00317"]],
        "Methanogenesis via methanol": [["K14080"], ["K04480"], ["K14081"]],
        "Methanogenesis via dimethylamine": [["K14082"], ["K16178"]],
        "Methanogenesis via dimethylsulfide, methanethiol, methylpropanoate": [
            ["K16954"],
            ["K16955"],
        ],
        "Methanogenesis via methylamine": [["K16178"]],
        "Methanogenesis via trimethylamine": [["K14083"]],
        "Methanogenesis via acetate": [["K00193"], ["K00194"], ["K00197"]],
        "Methanogenesis via CO2": [
            ["K00200"],
            ["K00201"],
            ["K00202"],
            ["K00203"],
            ["K00205"],
            ["K11261"],
            ["K00672"],
            ["K01499"],
            ["K13942"],
            ["K00320"],
            ["K00577"],
            ["K00578"],
            ["K00579"],
            ["K00580"],
            ["K00581"],
            ["K00582"],
            ["K00583"],
            ["K00584"],
        ],
        "Coenzyme M reduction to methane": [["K00399"], ["K00401"], ["K00402"]],
        "Coenzyme B/Coenzyme M regeneration": [
            ["K03388"],
            ["K03389"],
            ["K03390"],
            ["K08264"],
            ["K08265"],
        ],
    }

    # Scoring coefficients for pathways
    coefficients = {
        "Methanogenesis via methanol": 0.33,
        "Methanogenesis via dimethylamine": 0.50,
        "Methanogenesis via dimethylsulfide, methanethiol, methylpropanoate": 0.50,
        "Methanogenesis via acetate": 0.33,
        "Methanogenesis via CO2": 0.05,
        "Coenzyme M reduction to methane": 0.33,
        "Coenzyme B/Coenzyme M regeneration": 0.20,
        "dimethylamine/trimethylamine dehydrogenase": 1.00,
        "Methanogenesis via methylamine": 1.00,
        "Methanogenesis via trimethylamine": 1.00,
    }

    # Evaluate each pathway
    for pathway, ko_groups in pathway_kos.items():
        for group in ko_groups:
            if all(ko in ko_match for ko in group):
                out_data[pathway] += coefficients[pathway]

    # Adjust decimal places for specific pathways
    for pathway in ["Coenzyme B/Coenzyme M regeneration", "Methanogenesis via CO2"]:
        out_data[pathway] = round(out_data[pathway], 2)

    return out_data


def methane_ox(ko_match):
    """
    Computes the completeness of methane oxidation pathways based on KEGG Orthology (KO) identifiers.

    Args:
        ko_match (list): A list of KEGG Orthology (KO) identifiers.

    Returns:
        dict: A dictionary where keys represent methane oxidation pathways and values indicate their completeness (0.00 to 1.00).
    """

    # Initialize the output dictionary with methane oxidation pathways
    out_data = {
        "Soluble methane monooxygenase": 0,
        "Methanol dehydrogenase": 0,
        "Alcohol oxidase": 0,
    }

    # Define KO groups for each pathway
    pathway_kos = {
        "Soluble methane monooxygenase": ["K16157", "K16158", "K16159", "K16161"],
        "Methanol dehydrogenase": ["K14028", "K14029"],
        "Alcohol oxidase": ["K17066"],
    }

    # Contribution coefficients for pathways
    coefficients = {
        "Soluble methane monooxygenase": 0.25,
        "Methanol dehydrogenase": 0.50,
        "Alcohol oxidase": 1.00,
    }

    # Evaluate pathway completeness
    for pathway, kos in pathway_kos.items():
        for ko in kos:
            if ko in ko_match:
                out_data[pathway] += coefficients[pathway]

    # Adjust precision for output values
    for key in out_data:
        out_data[key] = round(out_data[key], 2)

    return out_data


def hydrogen(ko_match):
    """
    Computes the completeness of hydrogen-related pathways based on KEGG Orthology (KO) identifiers.

    Args:
        ko_match (list): A list of KEGG Orthology (KO) identifiers.

    Returns:
        dict: A dictionary where keys represent hydrogen pathways and values indicate their completeness (0.00 to 1.00).
    """

    # Initialize the output dictionary with hydrogen-related pathways
    out_data = {
        "NiFe hydrogenase": 0,
        "Membrane-bound hydrogenase": 0,
        "Ferredoxin hydrogenase": 0,
        "Hydrogen:quinone oxidoreductase": 0,
        "NAD-reducing hydrogenase": 0,
        "NADP-reducing hydrogenase": 0,
        "NiFe hydrogenase Hyd-1": 0,
    }

    # Define KO groups and their contribution coefficients
    pathway_kos = {
        "NiFe hydrogenase": [("K00437", "K18008")],
        "Membrane-bound hydrogenase": [("K18016", "K18017", "K18023")],
        "Ferredoxin hydrogenase": [("K00533", "K00534")],
        "Hydrogen:quinone oxidoreductase": [("K05922", "K05927")],
        "NAD-reducing hydrogenase": ["K00436", "K18005", "K18006", "K18007"],
        "NADP-reducing hydrogenase": ["K17992", "K18330", "K18331", "K18332"],
        "NiFe hydrogenase Hyd-1": ["K06282", "K06281", "K03620"],
    }

    coefficients = {
        "NiFe hydrogenase": 1.0,
        "Membrane-bound hydrogenase": 1.0,
        "Ferredoxin hydrogenase": 1.0,
        "Hydrogen:quinone oxidoreductase": 1.0,
        "NAD-reducing hydrogenase": 0.25,
        "NADP-reducing hydrogenase": 0.25,
        "NiFe hydrogenase Hyd-1": 0.33,
    }

    # Evaluate pathway completeness
    for pathway, kos in pathway_kos.items():
        if isinstance(kos[0], tuple):  # Group of KOs that must all match
            for group in kos:
                if all(ko in ko_match for ko in group):
                    out_data[pathway] = 1.0
        else:  # Individual KOs contributing fractions
            for ko in kos:
                if ko in ko_match:
                    out_data[pathway] += coefficients[pathway]

    # Adjust precision for output values
    for key in out_data:
        out_data[key] = round(out_data[key], 2)

    return out_data


def transporters(ko_match):
    """
    Calculate the presence of specific transporters based on KEGG Orthology (KO) matches.

    Args:
        ko_match (list): A list of KEGG Orthology IDs found in the dataset.

    Returns:
        dict: A dictionary with transporter categories as keys and their respective
              proportions (as a float between 0 and 1) as values.

    Notes:
        - Each transporter category is scored based on the presence of specific KO IDs.
        - If the KO IDs for a transporter are present, the score increases proportionally.
        - This function can be extended by adding new transporters and their KO IDs.
    """
    # Define transporter categories and their respective KO IDs
    transporter_kos = {
        "transporter: phosphate": ["K02040", "K02037", "K02038", "K02036"],
        "transporter: phosphonate": ["K02044", "K02042", "K02041"],
        "transporter: thiamin": ["K02064", "K02063", "K02062"],
        "transporter: vitamin B12": ["K06858", "K06073", "K06074"],
        "transporter: urea": ["K11959", "K11960", "K11961", "K11962", "K11963"],
    }

    # Define scoring fractions for each transporter
    scoring_fractions = {
        "transporter: phosphate": 0.25,
        "transporter: phosphonate": 0.33,
        "transporter: thiamin": 0.33,
        "transporter: vitamin B12": 0.33,
        "transporter: urea": 0.2,
    }

    # Initialize output dictionary with zero scores
    out_data = {key: 0 for key in transporter_kos.keys()}

    # Calculate scores for each transporter
    for transporter, kos in transporter_kos.items():
        for ko in kos:
            if ko in ko_match:
                out_data[transporter] += scoring_fractions[transporter]

    # Round scores to 2 decimal places for consistency
    for key in out_data:
        out_data[key] = round(out_data[key], 2)

    return out_data


def riboflavin(ko_match):
    """
    Calculate the proportion of riboflavin biosynthesis pathway components present
    based on KEGG Orthology (KO) matches.

    Args:
        ko_match (list): A list of KEGG Orthology IDs found in the dataset.

    Returns:
        dict: A dictionary with a single key "riboflavin biosynthesis" and a float value
              between 0 and 1 indicating the proportion of the pathway components present.

    Notes:
        - The pathway is divided into four key steps, each identified by specific KO IDs.
        - Additional steps can be uncommented or added in the future if needed.
    """
    # Define the KO groups corresponding to riboflavin biosynthesis steps
    ko_groups = {
        "ribB_ribAB": [
            "K02858",
            "K14652",
        ],  # Step 1: 3,4-dihydroxy 2-butanone 4-phosphate synthase
        "ribD_ribD2": ["K00082", "K11752"],  # Step 2: Uracil reductase/deaminase
        "ribH": ["K00794"],  # Step 3: 6,7-dimethyl-8-ribityllumazine synthase
        "ribE": ["K00793"],  # Step 4: Riboflavin synthase
        # Uncomment and adjust below for additional steps
        # "ribF_RF_FHY": ["K00861", "K20884", "K11753"],  # Riboflavin kinase or related
        # "FAD_synthetase": ["K14656", "K00953"],         # FAD synthetase
    }

    # Calculate the total number of steps present
    total_present = sum(
        any(ko in ko_match for ko in ko_list) for ko_list in ko_groups.values()
    )

    # Calculate the proportion of pathway steps present
    total_steps = len(ko_groups)
    riboflavin_score = round(total_present / total_steps, 2)

    return {"riboflavin biosynthesis": riboflavin_score}


def thiamin(ko_match):
    """
    Calculate the proportion of thiamin biosynthesis pathway components present
    based on KEGG Orthology (KO) matches.

    Args:
        ko_match (list): A list of KEGG Orthology IDs found in the dataset.

    Returns:
        dict: A dictionary with a single key "thiamin biosynthesis" and a float value
              between 0 and 1 indicating the proportion of the pathway components present.

    Notes:
        - The pathway is divided into 11 key steps, each identified by specific KO IDs.
        - New components or alternative KO IDs can easily be added by updating the `ko_groups` dictionary.
    """
    # Define the KO groups corresponding to thiamin biosynthesis steps
    ko_groups = {
        "thiF": ["K03148"],  # Sulfur carrier protein ThiS adenylyltransferase
        "iscS": ["K04487"],  # Cysteine desulfurase
        "thiH_thiO": ["K03150", "K03153"],  # 2-iminoacetate synthase or glycine oxidase
        "thiI": ["K03151"],  # Thiamine biosynthesis protein ThiI
        "dxs": ["K01662"],  # 1-deoxy-D-xylulose-5-phosphate synthase
        "thiG": ["K03149"],  # Thiazole synthase
        "tenI_THI4": [
            "K10810",
            "K03146",
        ],  # Thiazole tautomerase or thiamine thiazole synthase
        "THI5_thiC_THI20_thiD_thiDE": [
            "K18278",
            "K03147",
            "K00877",
            "K00941",
        ],  # Pyrimidine precursor enzymes
        "THI20_thiD": ["K00877", "K00941"],  # Hydroxymethylpyrimidine kinase
        "thiE_THI6": [
            "K00788",
            "K14153",
            "K14154",
        ],  # Thiamine-phosphate pyrophosphorylase
        "thiL": ["K00946"],  # Thiamine-monophosphate kinase
    }

    # Calculate the total number of steps present
    total_present = sum(
        any(ko in ko_match for ko in ko_list) for ko_list in ko_groups.values()
    )

    # Calculate the proportion of pathway steps present
    total_steps = len(ko_groups)
    thiamin_score = round(total_present / total_steps, 2)

    return {"thiamin biosynthesis": thiamin_score}


def cobalamin(ko_match):
    """
    Calculate the proportion of cobalamin biosynthesis pathway components present
    based on KEGG Orthology (KO) matches.

    Args:
        ko_match (list): A list of KEGG Orthology IDs found in the dataset.

    Returns:
        dict: A dictionary with a single key "cobalamin biosynthesis" and a float value
              between 0 and 1 indicating the proportion of the pathway components present.

    Notes:
        - The pathway is divided into 8 key steps, each identified by specific KO IDs.
        - New components or alternative KO IDs can easily be added by updating the `ko_groups` dictionary.
    """
    # Define the KO groups corresponding to cobalamin biosynthesis steps
    ko_groups = {
        "pduO_cobA": ["K00798", "K19221"],  # cob(I)alamin adenosyltransferase
        "cobQ": ["K02232"],  # adenosylcobyric acid synthase
        "cobC": ["K02225"],  # cobalamin biosynthetic protein CobC
        "cobD": ["K02227"],  # adenosylcobinamide-phosphate synthase
        "cobU": ["K02231"],  # adenosylcobinamide kinase / guanylyltransferase
        "cobY": [
            "K19712"
        ],  # adenosylcobinamide-phosphate guanylyltransferase (alternative)
        "cobV": ["K02233"],  # adenosylcobinamide-GDP ribazoletransferase
        "alpha_ribazole_phosphatase": ["K02226"],  # alpha-ribazole phosphatase
        "cobT": [
            "K00768"
        ],  # nicotinate-nucleotide--dimethylbenzimidazole phosphoribosyltransferase
    }

    # Calculate the total number of components present
    total_present = sum(
        any(ko in ko_match for ko in ko_list) for key, ko_list in ko_groups.items()
    )

    # Calculate the proportion of pathway components present
    total_steps = len(ko_groups)
    cobalamin_score = round(total_present / total_steps, 2)

    return {"cobalamin biosynthesis": cobalamin_score}


def oxidative_phosphorylation(ko_match):
    """
    Calculate the presence of components in the oxidative phosphorylation pathway
    based on KEGG Orthology (KO) matches.

    Args:
        ko_match (list): A list of KEGG Orthology IDs found in the dataset.

    Returns:
        dict: A dictionary with pathway components as keys and scores (proportions)
              between 0 and 1 as values.

    Notes:
        - Each pathway component is associated with specific KO IDs and a fractional score.
        - New components or alternative IDs can easily be added to the `ko_groups` dictionary.
    """
    # Define KO groups with associated weights for each pathway component
    ko_groups = {
        "F-type ATPase": (
            [
                "K02111",
                "K02112",
                "K02115",
                "K02113",
                "K02114",
                "K02108",
                "K02109",
                "K02110",
            ],
            0.125,
        ),
        "V-type ATPase": (
            [
                "K02117",
                "K02118",
                "K02119",
                "K02120",
                "K02121",
                "K02122",
                "K02107",
                "K02123",
                "K02124",
            ],
            0.11,
        ),
        "NADH-quinone oxidoreductase": (
            [
                "K00330",
                "K00331",
                "K00332",
                "K00333",
                "K00334",
                "K00335",
                "K00336",
                "K00337",
                "K00338",
                "K00339",
                "K00340",
                "K00341",
                "K00342",
                "K00343",
            ],
            0.07,
        ),
        "NAD(P)H-quinone oxidoreductase": (
            [
                "K05574",
                "K05582",
                "K05581",
                "K05579",
                "K05572",
                "K05580",
                "K05578",
                "K05576",
                "K05577",
                "K05575",
                "K05573",
                "K05583",
                "K05584",
                "K05585",
            ],
            0.07,
        ),
        "Cytochrome c oxidase, cbb3-type": (
            ["K00404", "K00405", "K00407", "K00406"],
            0.25,
        ),
        "Cytochrome bd complex": (["K00425", "K00426"], 0.5),
        "Cytochrome o ubiquinol oxidase": (
            ["K02300", "K02299", "K02298", "K02297"],
            0.25,
        ),
        "Cytochrome c oxidase": (["K02277", "K02276", "K02274", "K02275"], 0.25),
        "Cytochrome aa3-600 menaquinol oxidase": (
            ["K02829", "K02828", "K02827", "K02826"],
            0.25,
        ),
        "Na-NADH-ubiquinone oxidoreductase": (
            ["K00346", "K00347", "K00348", "K00349", "K00350", "K00351"],
            0.167,
        ),
    }

    # Initialize output data dictionary
    out_data = {key: 0 for key in ko_groups}

    # Calculate scores for each pathway component
    for component, (ko_list, weight) in ko_groups.items():
        for ko in ko_list:
            if ko in ko_match:
                out_data[component] += weight

    # Handle Ubiquinol-cytochrome c reductase separately due to special conditions
    if "K00411" in ko_match and "K00410" in ko_match:
        out_data["Ubiquinol-cytochrome c reductase"] = 1.0
    else:
        ubiquinol_ko = ["K00411", "K00412", "K00413"]
        out_data["Ubiquinol-cytochrome c reductase"] = round(
            sum(1 for ko in ubiquinol_ko if ko in ko_match) * 0.33, 2
        )

    # Round scores for consistency
    for key in out_data:
        out_data[key] = round(out_data[key], 2)

    return out_data


def photosynthesis(ko_match):
    """
    Calculate the presence of components in the photosynthesis pathway
    based on KEGG Orthology (KO) matches.

    Args:
        ko_match (list): A list of KEGG Orthology IDs found in the dataset.

    Returns:
        dict: A dictionary with pathway components as keys and scores (proportions)
              between 0 and 1 as values.
    """
    # Define KO groups with associated weights for each pathway component
    ko_groups = {
        "Photosystem II": (
            ["K02703", "K02706", "K02705", "K02704", "K02707", "K02708"],
            0.167,
        ),
        "Photosystem I": (
            [
                "K02689",
                "K02690",
                "K02691",
                "K02692",
                "K02693",
                "K02694",
                "K02696",
                "K02697",
                "K02698",
                "K02699",
                "K02700",
                "K08905",
                "K02695",
                "K02701",
                "K14332",
                "K02702",
            ],
            0.0625,
        ),
        "Cytochrome b6/f complex": (
            [
                "K02635",
                "K02637",
                "K02634",
                "K02636",
                "K02642",
                "K02643",
                "K03689",
                "K02640",
            ],
            0.125,
        ),
        "anoxygenic type-II reaction center": (["K08928", "K08929"], 0.5),
        "anoxygenic type-I reaction center": (
            ["K08940", "K08941", "K08942", "K08943"],
            0.25,
        ),
        "Retinal biosynthesis": (["K06443", "K02291", "K10027", "K13789"], 0.25),
    }

    # Initialize output data dictionary
    out_data = {key: 0 for key in ko_groups}
    out_data["Retinal from apo-carotenals"] = 0

    # Calculate scores for each pathway component
    for component, (ko_list, weight) in ko_groups.items():
        for ko in ko_list:
            if ko in ko_match:
                out_data[component] += weight

    # Handle "Retinal from apo-carotenals" separately due to its binary condition
    if "K00464" in ko_match:
        out_data["Retinal from apo-carotenals"] = 1

    # Round scores for consistency
    for key in out_data:
        out_data[key] = round(out_data[key], 2)

    return out_data


def entnerdoudoroff(ko_match):
    """
    Calculate the completeness of the Entner-Doudoroff Pathway based on KO matches.

    Args:
        ko_match (list): A list of KEGG Orthology IDs found in the dataset.

    Returns:
        dict: A dictionary with the pathway name as the key and its completeness score (0-1) as the value.
    """
    # Define KO groups for the pathway
    pathway_1 = {
        "H6PD": ["K13937"],  # Hexose-6-phosphate dehydrogenase
        "edd": ["K01690"],  # Phosphogluconate dehydratase
        "aldolase": [
            "K01625",
            "K17463",
            "K11395",
        ],  # 2-dehydro-3-deoxyphosphogluconate aldolase
    }

    pathway_2 = {
        "G6PD": ["K00036"],  # Glucose-6-phosphate 1-dehydrogenase
        "6PGL": ["K01057", "K07404"],  # 6-phosphogluconolactonase
        "edd": ["K01690"],  # Phosphogluconate dehydratase
        "aldolase": [
            "K01625",
            "K17463",
            "K11395",
        ],  # 2-dehydro-3-deoxyphosphogluconate aldolase
    }

    # Check if pathway 1 is applicable (H6PD present)
    if any(ko in ko_match for ko in pathway_1["H6PD"]):
        total = sum(
            any(ko in ko_match for ko in pathway_1[component])
            for component in pathway_1
        )
        value = total / 3  # Pathway 1 has 3 components
    else:
        # Check pathway 2 (alternative pathway)
        total = sum(
            any(ko in ko_match for ko in pathway_2[component])
            for component in pathway_2
        )
        value = total / 4  # Pathway 2 has 4 components

    # Return the result
    return {"Entner-Doudoroff Pathway": round(value, 2)}


def mixedacid(ko_match):
    """
    Calculate the completeness of the Mixed Acid Fermentation pathways based on KO matches.

    Args:
        ko_match (list): A list of KEGG Orthology IDs found in the dataset.

    Returns:
        dict: A dictionary with pathway steps as keys and completeness scores (0-1) as values.
    """
    out_data = {
        "Mixed acid: Lactate": 0,
        "Mixed acid: Formate": 0,
        "Mixed acid: Formate to CO2 & H2": 0,
        "Mixed acid: Acetate": 0,
        "Mixed acid: Ethanol, Acetate to Acetylaldehyde": 0,
        "Mixed acid: Ethanol, Acetyl-CoA to Acetylaldehyde (reversible)": 0,
        "Mixed acid: Ethanol, Acetylaldehyde to Ethanol": 0,
        "Mixed acid: PEP to Succinate via OAA, malate & fumarate": 0,
    }

    # Define the KO groups for each step
    steps = {
        "Mixed acid: Lactate": ["K00016"],  # L-lactate dehydrogenase
        "Mixed acid: Formate": ["K00656"],  # Formate C-acetyltransferase
        "Mixed acid: Formate to CO2 & H2": [
            "K00122",
            "K00125",
            "K00126",
            "K00123",
            "K00124",
            "K00127",
        ],  # Formate dehydrogenase
        "Mixed acid: Acetate": [
            "K00156",
            "K00158",
            "K01512",
            "K01067",
            "K13788",
            "K04020",
            "K00467",
        ],  # Acetate-related enzymes
        "Mixed acid: Ethanol, Acetate to Acetylaldehyde": [
            "K00128",
            "K14085",
            "K00149",
            "K00129",
            "K00138",
        ],  # Aldehyde dehydrogenases
        "Mixed acid: Ethanol, Acetyl-CoA to Acetylaldehyde (reversible)": [
            "K00132",
            "K04072",
            "K04073",
            "K18366",
            "K04021",
        ],  # Acetaldehyde dehydrogenases
        "Mixed acid: Ethanol, Acetylaldehyde to Ethanol": [
            "K13951",
            "K13980",
            "K13952",
            "K13953",
            "K13954",
            "K00001",
            "K00121",
            "K04072",
            "K18857",
            "K00114",
            "K00002",
            "K04022",
        ],  # Alcohol dehydrogenases
        "Mixed acid: PEP to Succinate via OAA, malate & fumarate": [
            "K01596",
            "K20370",
            "K01610",  # PEPCK
            "K00051",
            "K00116",  # Malate dehydrogenases
            "K00025",
            "K00026",
            "K00024",  # Additional malate dehydrogenases
            "K01676",
            "K01677",
            "K01678",
            "K01679",  # Fumarate hydratases
            "K00244",
            "K00245",
            "K00246",
            "K00247",  # Fumarate reductases
        ],
    }

    # Define scoring for individual pathways
    scoring = {
        "Mixed acid: Formate to CO2 & H2": 1 / 6,
        "Mixed acid: PEP to Succinate via OAA, malate & fumarate": {
            "main": 0.25,
            "additional_malate": 0.083,
            "fumarate_hydratase": 0.0625,
            "fumarate_reductase": 0.0625,
        },
    }

    # Process each step
    for step, ko_list in steps.items():
        if step == "Mixed acid: Acetate":
            if "K00156" in ko_match:
                out_data[step] = 1
            elif any(ko in ko_match for ko in ["K00158", "K01512", "K13788", "K04020"]):
                out_data[step] += 0.5
        elif step == "Mixed acid: Ethanol, Acetylaldehyde to Ethanol":
            if any(ko in ko_match for ko in steps[step]):
                out_data[step] = 1
            elif any(
                ko in ko_match for ko in ["K14028", "K14029"]
            ):  # Methanol dehydrogenases
                out_data[step] += 0.5
        elif step == "Mixed acid: Formate to CO2 & H2":
            out_data[step] += sum(ko in ko_match for ko in ko_list) * scoring[step]
        elif step == "Mixed acid: PEP to Succinate via OAA, malate & fumarate":
            if any(ko in ko_match for ko in ["K01596", "K20370", "K01610"]):
                out_data[step] += scoring[step]["main"]
            if any(ko in ko_match for ko in ["K00051", "K00116"]):
                out_data[step] += scoring[step]["main"]
            else:
                out_data[step] += (
                    sum(ko in ko_match for ko in ["K00025", "K00026", "K00024"])
                    * scoring[step]["additional_malate"]
                )
            out_data[step] += (
                sum(ko in ko_match for ko in ["K01676", "K01677", "K01678", "K01679"])
                * scoring[step]["fumarate_hydratase"]
            )
            out_data[step] += (
                sum(ko in ko_match for ko in ["K00244", "K00245", "K00246", "K00247"])
                * scoring[step]["fumarate_reductase"]
            )
        else:
            if any(ko in ko_match for ko in ko_list):
                out_data[step] = 1

    return out_data


def naphthalene(ko_match):
    """
    Calculate the completeness of the Naphthalene degradation pathway based on KO matches.

    Args:
        ko_match (list): A list of KEGG Orthology IDs found in the dataset.

    Returns:
        dict: A dictionary with the pathway and its completeness score (0-1).
    """
    # Initialize total completeness score
    total = 0

    # Define KO groups for each step in the pathway
    steps = {
        "nahAabcd": [
            "K14579",
            "K14580",
            "K14578",
            "K14581",
        ],  # Naphthalene 1,2-dioxygenase
        "nahB": ["K14582"],  # cis-1,2-dihydro-1,2-dihydroxynaphthalene dehydrogenase
        "nahC": ["K14583"],  # 1,2-dihydroxynaphthalene dioxygenase
        "nahD": ["K14584"],  # 2-hydroxychromene-2-carboxylate isomerase
        "nahE": ["K14585"],  # trans-o-hydroxybenzylidenepyruvate hydratase-aldolase
        "nahF": ["K00152"],  # Salicylaldehyde dehydrogenase
    }

    # Scoring for multi-subunit enzymes
    for ko in steps["nahAabcd"]:
        if ko in ko_match:
            total += 0.25

    # Scoring for single KO enzymes
    for step, kos in steps.items():
        if step != "nahAabcd" and any(ko in ko_match for ko in kos):
            total += 1

    # Calculate the completeness as a fraction of the total possible score
    value = round(total / 6, 2)

    return {"Naphthalene degradation to salicylate": value}


def biofilm(ko_match):
    """
    Calculate the presence of various biofilm-related pathways based on KO identifiers.

    Parameters:
    ko_match (list): List of KO identifiers to check against biofilm-related pathways.

    Returns:
    dict: A dictionary with keys representing biofilm pathways and values indicating
          their calculated presence (0 to 1 scale for partial pathways, 1 for complete pathways).
    """
    # Initialize output dictionary with default values
    out_data = {
        "Biofilm PGA Synthesis protein": 0,
        "Colanic acid and Biofilm transcriptional regulator": 0,
        "Biofilm regulator BssS": 0,
        "Colanic acid and Biofilm protein A": 0,
        "Curli fimbriae biosynthesis": 0,
        "Adhesion": 0,
    }

    # Biofilm PGA Synthesis protein: 4 components, each contributing 0.25
    pga_synthesis_ko = ["K11935", "K11931", "K11936", "K11937"]
    for ko in pga_synthesis_ko:
        if ko in ko_match:
            out_data["Biofilm PGA Synthesis protein"] += 0.25

    # Colanic acid and Biofilm transcriptional regulator: Single identifier
    if "K13654" in ko_match:
        out_data["Colanic acid and Biofilm transcriptional regulator"] = 1

    # Biofilm regulator BssS: Single identifier
    if "K12148" in ko_match:
        out_data["Biofilm regulator BssS"] = 1

    # Colanic acid and Biofilm protein A: Single identifier
    if "K13650" in ko_match:
        out_data["Colanic acid and Biofilm protein A"] = 1

    # Curli fimbriae biosynthesis: 3 components, each contributing 0.33
    curli_biosynthesis_ko = ["K04335", "K04334", "K04336"]
    for ko in curli_biosynthesis_ko:
        if ko in ko_match:
            out_data["Curli fimbriae biosynthesis"] += 0.33

    # Adhesion: Single identifier
    if "K12687" in ko_match:
        out_data["Adhesion"] = 1

    return out_data


def competence(ko_match):
    """
    Calculate the presence of competence-related pathways based on KO identifiers.

    Parameters:
    ko_match (list): List of KO identifiers to check against competence-related pathways.

    Returns:
    dict: A dictionary with keys representing competence-related components
          and values indicating their calculated presence (0 to 1 scale).
    """
    # Initialize output dictionary with default values
    out_data = {
        "Competence-related core components": 0,
        "Competence-related related components": 0,
        "Competence factors": 0,
    }

    # Competence-related core components: 14 components, each contributing 0.07
    competence_core_ko = [
        "K02237",
        "K01493",
        "K02238",
        "K02239",
        "K02240",
        "K02241",
        "K02242",
        "K02243",
        "K02244",
        "K02245",
        "K02246",
        "K02247",
        "K02248",
        "K02249",
    ]
    for ko in competence_core_ko:
        if ko in ko_match:
            out_data["Competence-related core components"] += 0.07

    # Competence-related related components: 5 components, each contributing 0.2
    competence_related_ko = ["K02250", "K02251", "K02252", "K02253", "K02254"]
    for ko in competence_related_ko:
        if ko in ko_match:
            out_data["Competence-related related components"] += 0.2

    # Competence factors: 7 components, each contributing 0.14
    competence_factors_ko = [
        "K12292",
        "K07680",
        "K12293",
        "K12415",
        "K12294",
        "K12295",
        "K12296",
    ]
    for ko in competence_factors_ko:
        if ko in ko_match:
            out_data["Competence factors"] += 0.14

    return out_data


def anaplerotic(ko_match):
    """
    Calculate the presence of anaplerotic pathways based on KO identifiers.

    Parameters:
    ko_match (list): List of KO identifiers to check against anaplerotic pathways.

    Returns:
    dict: A dictionary with keys representing pathways (e.g., "Glyoxylate shunt",
          "Anaplerotic genes") and values indicating their calculated presence (0 to 1 scale).
    """
    # Initialize output dictionary with default values
    out_data = {
        "Glyoxylate shunt": 0,
        "Anaplerotic genes": 0,
    }

    # Glyoxylate shunt: requires both isocitrate lyase and malate synthase
    glyoxylate_ko = ["K01637", "K01638"]
    if all(ko in ko_match for ko in glyoxylate_ko):
        out_data["Glyoxylate shunt"] = 1

    # Anaplerotic genes and their contribution weights
    anaplerotic_ko_weights = {
        "K00029": 0.25,  # Malate dehydrogenase (oxaloacetate-decarboxylating) (NADP+)
        "K01595": 0.25,  # Phosphoenolpyruvate carboxylase
        "K01610": 0.25,  # Phosphoenolpyruvate carboxykinase (ATP)
        "K01596": 0.25,  # Phosphoenolpyruvate carboxykinase (GTP)
        "K20370": 0.25,  # Phosphoenolpyruvate carboxykinase (diphosphate)
        "K01958": 0.25,  # Pyruvate carboxylase (single subunit form)
        # Pyruvate carboxylase (multi-subunit form requires both subunits)
        "K01959_K01960": 0.25,
    }

    for ko, weight in anaplerotic_ko_weights.items():
        if "_" in ko:  # Special handling for multi-subunit requirement
            subunits = ko.split("_")
            if all(subunit in ko_match for subunit in subunits):
                out_data["Anaplerotic genes"] += weight
        elif ko in ko_match:
            out_data["Anaplerotic genes"] += weight

    return out_data


def sulfolipid(ko_match):
    """
    Calculate the presence of sulfolipid biosynthesis pathway based on KO identifiers.

    Parameters:
    ko_match (list): List of KO identifiers to check against sulfolipid biosynthesis genes.

    Returns:
    dict: A dictionary with a key "Sulfolipid biosynthesis" indicating its calculated presence (0 to 1 scale).
    """
    # Initialize output dictionary with default value
    out_data = {"Sulfolipid biosynthesis": 0}

    # KO identifiers and their contribution weights for sulfolipid biosynthesis
    sulfolipid_ko_weights = {
        "K06118": 0.5,  # First enzyme involved in sulfolipid biosynthesis
        "K06119": 0.5,  # Second enzyme involved in sulfolipid biosynthesis
    }

    # Increment the pathway score based on matching KOs
    for ko, weight in sulfolipid_ko_weights.items():
        if ko in ko_match:
            out_data["Sulfolipid biosynthesis"] += weight

    return out_data


def cplyase(ko_match):
    """
    Evaluate the presence of C-P lyase-related components based on KO identifiers.

    Parameters:
    ko_match (list): List of KO identifiers to check against C-P lyase-related genes.

    Returns:
    dict: A dictionary containing the calculated presence of:
        - "C-P lyase cleavage PhnJ"
        - "CP-lyase complex"
        - "CP-lyase operon"
    """
    # Initialize output dictionary with default values
    out_data = {
        "C-P lyase cleavage PhnJ": 0,
        "CP-lyase complex": 0,
        "CP-lyase operon": 0,
    }

    # Mapping KO identifiers to their contributions
    phnJ_ko = "K06163"  # Specific KO identifier for PhnJ
    complex_kos = [
        "K06163",
        "K06164",
        "K06165",
        "K06166",
    ]  # KOs for the CP-lyase complex
    operon_kos = [
        "K06163",
        "K06164",
        "K06165",
        "K06166",
        "K05780",
        "K06162",
        "K06167",
        "K09994",
        "K05774",
        "K05781",
        "K02043",
    ]  # KOs for the full CP-lyase operon

    # Evaluate C-P lyase cleavage PhnJ
    if phnJ_ko in ko_match:
        out_data["C-P lyase cleavage PhnJ"] = 1

    # Evaluate CP-lyase complex
    for ko in complex_kos:
        if ko in ko_match:
            out_data["CP-lyase complex"] += 0.25

    # Evaluate CP-lyase operon
    for ko in operon_kos:
        if ko in ko_match:
            out_data["CP-lyase operon"] += 0.09

    return out_data


def secretion(ko_match):
    """
    Evaluate the presence of bacterial secretion system components based on KO identifiers.

    Parameters:
    ko_match (list): List of KO identifiers to check against various secretion systems.

    Returns:
    dict: A dictionary containing the calculated presence for:
        - Type I, II, III, IV, Vabc, and VI Secretion systems
        - Sec-SRP
        - Twin Arginine Targeting (TAT)
    """
    # Initialize output dictionary
    out_data = {
        "Type I Secretion": 0,
        "Type III Secretion": 0,
        "Type II Secretion": 0,
        "Type IV Secretion": 0,
        "Type VI Secretion": 0,
        "Sec-SRP": 0,
        "Twin Arginine Targeting": 0,
        "Type Vabc Secretion": 0,
    }

    # Define KO groups
    secretion_kos = {
        "Type I Secretion": (["K12340", "K11003", "K11004"], 0.33),
        "Type III Secretion": (
            [
                "K03221",
                "K04056",
                "K04057",
                "K04059",
                "K03219",
                "K04058",
                "K03222",
                "K03226",
                "K03227",
                "K03228",
                "K03229",
                "K03230",
                "K03224",
                "K03225",
                "K03223",
            ],
            0.0666,
        ),
        "Type II Secretion": (
            [
                "K02453",
                "K02465",
                "K02452",
                "K02455",
                "K02456",
                "K02457",
                "K02458",
                "K02459",
                "K02460",
                "K02461",
                "K02462",
                "K02454",
                "K02464",
            ],
            0.0769,
        ),
        "Type IV Secretion": (
            [
                "K03194",
                "K03197",
                "K03198",
                "K03200",
                "K03202",
                "K03204",
                "K03201",
                "K03203",
                "K03195",
                "K03199",
                "K03196",
                "K03205",
            ],
            0.083,
        ),
        "Type VI Secretion": (
            [
                "K11904",
                "K11903",
                "K11906",
                "K11891",
                "K11892",
                "K11907",
                "K11912",
                "K11913",
                "K11915",
            ],
            0.111,
        ),
        "Twin Arginine Targeting": (["K03116", "K03117", "K03118", "K03425"], 0.25),
        "Type Vabc Secretion": (
            ["K11028", "K11017", "K11016", "K12341", "K12342"],
            0.2,
        ),
    }

    # Process each secretion type
    for key, (kos, increment) in secretion_kos.items():
        for ko in kos:
            if ko in ko_match:
                out_data[key] += increment

    # Special cases for Sec-SRP
    secsrp_sets = [
        (
            ["K03072", "K03074"],
            [
                "K03072",
                "K03074",
                "K03073",
                "K03075",
                "K03076",
                "K03210",
                "K03217",
                "K03070",
                "K13301",
                "K03110",
                "K03071",
                "K03106",
            ],
            0.083,
        ),
        (
            ["K12257"],
            [
                "K12257",
                "K03073",
                "K03075",
                "K03076",
                "K03210",
                "K03217",
                "K03070",
                "K13301",
                "K03110",
                "K03071",
                "K03106",
            ],
            0.09,
        ),
    ]

    for trigger_kos, secsrp_kos, increment in secsrp_sets:
        if any(ko in ko_match for ko in trigger_kos):
            out_data["Sec-SRP"] = 0
            for ko in secsrp_kos:
                if ko in ko_match:
                    out_data["Sec-SRP"] += increment

    return out_data


def serine(ko_match):
    """
    Calculate the completeness of the serine pathway for formaldehyde assimilation
    based on provided KO identifiers.

    Parameters:
    ko_match (list): List of KO identifiers to check for the serine pathway components.

    Returns:
    dict: A dictionary with the completeness of the serine pathway as a fraction.
        - Key: "Serine pathway/formaldehyde assimilation"
    """
    # Initialize output dictionary
    out_data = {"Serine pathway/formaldehyde assimilation": 0}

    # KO identifiers for the serine pathway
    serine_pathway_kos = [
        "K00600",
        "K00830",
        "K00018",
        "K11529",
        "K01689",
        "K01595",
        "K00024",
        "K08692",
        "K14067",
    ]

    # Calculate pathway completeness
    for ko in serine_pathway_kos:
        if ko in ko_match:
            out_data["Serine pathway/formaldehyde assimilation"] += 0.1

    return out_data


def arsenic(ko_match):
    """
    Calculate the completeness of the arsenic reduction pathway
    based on provided KO identifiers.

    Parameters:
    ko_match (list): List of KO identifiers to check for arsenic reduction components.

    Returns:
    dict: A dictionary with the completeness of the arsenic reduction pathway as a fraction.
        - Key: "Arsenic reduction"
    """
    # Initialize output dictionary
    out_data = {"Arsenic reduction": 0}

    # KO identifiers for arsenic reduction pathway
    arsC_kos = {"K00537", "K03741", "K18701"}  # Arsenate reductase (arsC)
    arsB_kos = {"K03325", "K03893"}  # Arsenite transporter (arsB)
    arsR_kos = {"K03892"}  # Transcriptional regulator (arsR)
    arsA_kos = {"K01551"}  # Arsenite pump-driving ATPase (arsA)

    # Calculate pathway completeness
    if arsC_kos.intersection(ko_match):
        out_data["Arsenic reduction"] += 0.25
    if arsB_kos.intersection(ko_match):
        out_data["Arsenic reduction"] += 0.25
    if arsR_kos.intersection(ko_match):
        out_data["Arsenic reduction"] += 0.25
    if arsA_kos.intersection(ko_match):
        out_data["Arsenic reduction"] += 0.25

    return out_data


def metal_transport(ko_match):
    """
    Determine the completeness of metal transport systems based on provided KO identifiers.

    Parameters:
    ko_match (list): List of KO identifiers to check for metal transporter components.

    Returns:
    dict: A dictionary with completeness values for various metal transport systems.
        - Keys represent specific transporters.
        - Values are fractions or 1.0 indicating the presence of components.
    """
    # Initialize the output dictionary
    out_data = {
        "Cobalt transporter CbiMQ": 0,
        "Cobalt transporter CbtA": 0,
        "Cobalt transporter CorA": 0,
        "Nickel ABC-type substrate-binding NikA": 0,
        "Copper transporter CopA": 0,
        "Ferrous iron transporter FeoB": 0,
        "Ferric iron ABC-type substrate-binding AfuA": 0,
        "Fe-Mn transporter MntH": 0,
    }

    # Define KO groups for each transporter
    cbi_mq_kos = {"K02007", "K02008"}  # Cobalt transporter CbiMQ
    cbt_a_kos = {"K18837"}  # Cobalt transporter CbtA
    cor_a_kos = {"K03284"}  # Cobalt transporter CorA
    nik_a_kos = {"K15584"}  # Nickel ABC-type substrate-binding NikA
    cop_a_kos = {"K17686"}  # Copper transporter CopA
    feo_b_kos = {"K04759"}  # Ferrous iron transporter FeoB
    afu_a_kos = {"K02012"}  # Ferric iron ABC-type substrate-binding AfuA
    mnt_h_kos = {"K03322"}  # Fe-Mn transporter MntH

    # Check for transporter components in KO matches
    out_data["Cobalt transporter CbiMQ"] = sum(
        0.5 for ko in cbi_mq_kos if ko in ko_match
    )
    out_data["Cobalt transporter CbtA"] = 1.0 if cbt_a_kos.intersection(ko_match) else 0
    out_data["Cobalt transporter CorA"] = 1.0 if cor_a_kos.intersection(ko_match) else 0
    out_data["Nickel ABC-type substrate-binding NikA"] = (
        1.0 if nik_a_kos.intersection(ko_match) else 0
    )
    out_data["Copper transporter CopA"] = 1.0 if cop_a_kos.intersection(ko_match) else 0
    out_data["Ferrous iron transporter FeoB"] = (
        1.0 if feo_b_kos.intersection(ko_match) else 0
    )
    out_data["Ferric iron ABC-type substrate-binding AfuA"] = (
        1.0 if afu_a_kos.intersection(ko_match) else 0
    )
    out_data["Fe-Mn transporter MntH"] = 1.0 if mnt_h_kos.intersection(ko_match) else 0

    return out_data


def amino_acids(ko_match):
    """
    Identifies and quantifies the presence of genes related to amino acid biosynthesis
    based on KEGG Orthology (KO) identifiers.

    Parameters:
        ko_match (list): List of KO identifiers to be analyzed.

    Returns:
        dict: A dictionary with keys representing amino acids and values indicating
              their synthesis presence or contribution (0 to 1 scale).
    """
    out_data = {
        "histidine": 0,
        "arginine": 0,
        "lysine": 0,
        "serine": 0,
        "threonine": 0,
        "asparagine": 0,
        "glutamine": 0,
        "cysteine": 0,
        "glycine": 0,
        "proline": 0,
        "alanine": 0,
        "valine": 0,
        "methionine": 0,
        "phenylalanine": 0,
        "isoleucine": 0,
        "leucine": 0,
        "tryptophan": 0,
        "tyrosine": 0,
        "aspartate": 0,
        "glutamate": 0,
    }

    # Histidine
    if "K00013" in ko_match:
        out_data["histidine"] = 1

    # Arginine
    if "K01755" in ko_match or "K14681" in ko_match:
        out_data["arginine"] = 1

    # Asparagine
    if "K01913" in ko_match or "K01953" in ko_match:
        out_data["asparagine"] = 1

    # Lysine
    lysine_ko = {"K01586", "K12526", "K05831", "K00290"}
    out_data["lysine"] = any(ko in ko_match for ko in lysine_ko)

    # Serine
    serine_ko = {"K01079", "K02203", "K02205", "K00600"}
    if any(ko in ko_match for ko in serine_ko):
        out_data["serine"] = 1
    if "K00600" in ko_match:
        out_data["glycine"] = 1

    # Threonine
    threonine_ko = {"K01733", "K01620"}
    if any(ko in ko_match for ko in threonine_ko):
        out_data["threonine"] = 1
        if "K01620" in ko_match:
            out_data["glycine"] = 1

    # Glutamine
    if "K01915" in ko_match:
        out_data["glutamine"] = 1

    # Cysteine
    cysteine_ko = {"K01758", "K17217", "K01738", "K10150", "K12339"}
    out_data["cysteine"] = any(ko in ko_match for ko in cysteine_ko)

    # Proline
    if "K00286" in ko_match or "K01750" in ko_match:
        out_data["proline"] = 1

    # Alanine
    alanine_ko = {"K14260", "K09758", "K00259", "K19244"}
    out_data["alanine"] = any(ko in ko_match for ko in alanine_ko)

    # Valine & Isoleucine
    valine_isoleucine_ko = {"K00826", "K01687", "K00053", "K01652", "K01653", "K11258"}
    for ko in valine_isoleucine_ko:
        if ko in ko_match:
            out_data["valine"] += 0.166
            out_data["isoleucine"] += 0.166

    # Leucine
    leucine_ko = {"K00826", "K00052", "K01703", "K01649"}
    for ko in leucine_ko:
        if ko in ko_match:
            out_data["leucine"] += 0.25

    # Methionine
    if "K00549" in ko_match or "K00548" in ko_match:
        out_data["methionine"] = 1

    # Phenylalanine & Tyrosine
    phenyl_tyrosine_ko = {"K00832", "K00838"}
    if any(ko in ko_match for ko in phenyl_tyrosine_ko):
        out_data["phenylalanine"] = 1
        out_data["tyrosine"] = 1

    # Phenylalanine
    phenylalanine_ko = {"K04518", "K05359", "K01713"}
    out_data["phenylalanine"] = any(ko in ko_match for ko in phenylalanine_ko)

    # Tyrosine
    tyrosine_ko = {"K15226", "K24018", "K00220"}
    out_data["tyrosine"] = any(ko in ko_match for ko in tyrosine_ko)

    # Tryptophan
    if "K01695" in ko_match:
        out_data["tryptophan"] += 0.5
    if "K01696" in ko_match or "K06001" in ko_match:
        out_data["tryptophan"] += 0.5

    # Aspartate & Glutamate
    aspartate_glutamate_ko = {
        "K00811",
        "K00812",
        "K00813",
        "K11358",
        "K14454",
        "K14455",
    }
    if any(ko in ko_match for ko in aspartate_glutamate_ko):
        out_data["aspartate"] = 1
        out_data["glutamate"] = 1

    return out_data


def plastic(ko_match):
    """
    Identifies and quantifies the presence of genes related to PET (polyethylene terephthalate) degradation
    based on KEGG Orthology (KO) identifiers.

    Parameters:
        ko_match (list): List of KO identifiers to be analyzed.

    Returns:
        dict: A dictionary with a single key "PET degradation" and a value indicating the
              degradation contribution (0 to 1 scale).
    """
    out_data = {"PET degradation": 0}

    # Poly(ethylene terephthalate) hydrolase and related enzymes
    pet_hydrolase_ko = {"K21104", "K21105", "K18076"}
    for ko in pet_hydrolase_ko:
        if ko in ko_match:
            out_data["PET degradation"] += 0.25

    # Terephthalate 1,2-dioxygenase oxygenase (two possible variants)
    if "K18077" in ko_match or ("K18074" in ko_match and "K18075" in ko_match):
        out_data["PET degradation"] += 0.25

    return out_data


def carbon_storage(ko_match):
    """
    Identifies and quantifies the presence of genes involved in carbon storage pathways,
    including starch/glycogen synthesis and degradation, and polyhydroxybutyrate synthesis.

    Parameters:
        ko_match (list): List of KO identifiers to be analyzed.

    Returns:
        dict: A dictionary with contributions to:
              - "starch/glycogen synthesis"
              - "starch/glycogen degradation"
              - "polyhydroxybutyrate synthesis"
    """
    out_data = {
        "starch/glycogen synthesis": 0,
        "starch/glycogen degradation": 0,
        "polyhydroxybutyrate synthesis": 0,
    }

    # Starch/Glycogen Synthesis
    starch_synthesis_ko = {"K00703", "K00975"}
    for ko in starch_synthesis_ko:
        if ko in ko_match:
            out_data["starch/glycogen synthesis"] += 0.33

    if "K00700" in ko_match or "K16149" in ko_match:
        out_data["starch/glycogen synthesis"] += 0.33

    # Starch/Glycogen Degradation
    starch_degradation_ko = {
        "K21574",  # glucan 1,4-alpha-glucosidase
        "K00701",  # cyclomaltodextrin glucanotransferase
        "K01214",  # isoamylase
        "K00688",
        "K16153",
        "K00705",
        "K22451",
        "K02438",
        "K01200",  # starch > glucose-6P
        "K01176",
        "K05343",  # alpha-amylase
        "K01177",  # beta-amylase
        "K05992",
        "K01208",  # maltogenic alpha-amylase
    }
    if any(ko in ko_match for ko in starch_degradation_ko):
        out_data["starch/glycogen degradation"] = 1

    # Polyhydroxybutyrate Synthesis
    if "K00023" in ko_match:
        out_data["polyhydroxybutyrate synthesis"] += 0.5

    phb_ko = {"K00626", "K03821", "K22881"}
    for ko in phb_ko:
        if ko in ko_match:
            out_data["polyhydroxybutyrate synthesis"] += 0.167

    return out_data


def phosphate_storage(ko_match):
    """
    Identifies and quantifies the presence of genes involved in bidirectional polyphosphate storage.

    Parameters:
        ko_match (list): List of KO identifiers to be analyzed.

    Returns:
        dict: A dictionary with contributions to "bidirectional polyphosphate" storage.
    """
    out_data = {"bidirectional polyphosphate": 0}

    # Bidirectional polyphosphate synthesis and degradation
    polyphosphate_ko_set1 = {"K00937", "K22468"}
    polyphosphate_ko_set2 = {"K01507", "K15986", "K06019"}

    # Check and increment for each set
    if any(ko in ko_match for ko in polyphosphate_ko_set1):
        out_data["bidirectional polyphosphate"] += 0.5
    if any(ko in ko_match for ko in polyphosphate_ko_set2):
        out_data["bidirectional polyphosphate"] += 0.5

    return out_data


def carotenoids(ko_match):
    """
    Identifies and quantifies the presence of genes involved in carotenoid biosynthesis pathways and
    their end products.

    Parameters:
        ko_match (list): List of KO identifiers to be analyzed.

    Returns:
        dict: A dictionary with contributions to various carotenoid biosynthesis pathways
              and their end products.
    """
    out_data = {
        "carotenoids backbone biosynthesis": 0,
        "end-product astaxanthin": 0,
        "end-product nostoxanthin": 0,
        "end-product zeaxanthin diglucoside": 0,
        "end-product myxoxanthophylls": 0,
        "staphyloaxanthin biosynthesis": 0,
        "mevalonate pathway": 0,
        "MEP-DOXP pathway": 0,
    }

    # Staphyloaxanthin biosynthesis pathway
    staphyloaxanthin_ko = {"K10208", "K10209", "K10210", "K00128", "K10211", "K10212"}
    out_data["staphyloaxanthin biosynthesis"] += sum(
        0.167 for ko in staphyloaxanthin_ko if ko in ko_match
    )

    # Mevalonate pathway
    mevalonate_ko = {"K01641", "K00054", "K00869", "K00938", "K01597"}
    out_data["mevalonate pathway"] += sum(0.2 for ko in mevalonate_ko if ko in ko_match)

    # MEP-DOXP pathway
    mepdoxp_ko = {"K01662", "K00099", "K00991", "K00919", "K01770", "K03526", "K03527"}
    out_data["MEP-DOXP pathway"] += sum(0.142 for ko in mepdoxp_ko if ko in ko_match)

    # Carotenoids backbone biosynthesis
    backbone_ko = {"K23155", "K02291", "K00514"}
    out_data["carotenoids backbone biosynthesis"] += sum(
        0.2 for ko in backbone_ko if ko in ko_match
    )
    if "K06443" in ko_match or "K14606" in ko_match:
        out_data["carotenoids backbone biosynthesis"] += 0.2

    # End-product nostoxanthin
    if "K02294" in ko_match:
        out_data["end-product nostoxanthin"] = 1

    # End-product zeaxanthin diglucoside
    if "K02294" in ko_match and "K14596" in ko_match:
        out_data["end-product zeaxanthin diglucoside"] = 1

    # End-product astaxanthin
    if "K09836" in ko_match or "K02292" in ko_match:
        out_data["end-product astaxanthin"] = 1

    # End-product myxoxanthophylls
    myxoxanthophylls_ko = {"K08977", "K02294", "K00721"}
    out_data["end-product myxoxanthophylls"] += sum(
        0.33 for ko in myxoxanthophylls_ko if ko in ko_match
    )

    return out_data


def main():
    """
    Main function to process KEGG_ko column in input file, compute functional annotations,
    and generate an output file with a heat map data structure.
    """

    matplotlib.use("Agg")

    # Argument parser setup
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
    )
    args = parser.parse_args()

    # Parse input file into genome data
    genome_data = {}
    with open(args.input, "r") as infile:
        for line in infile:
            line = line.strip()
            if not line:
                continue
            genome, ko = line.split()[0].split("_")[0], line.split()[1]
            genome_data.setdefault(genome, []).append(ko)

    # Order of functions in output
    function_order = [
        "glycolysis",
        "gluconeogenesis",
        "TCA Cycle",
        "NAD(P)H-quinone oxidoreductase",
        "NADH-quinone oxidoreductase",
        "Na-NADH-ubiquinone oxidoreductase",
        "F-type ATPase",
        "V-type ATPase",
        "Cytochrome c oxidase",
        "Ubiquinol-cytochrome c reductase",
        "Cytochrome o ubiquinol oxidase",
        "Cytochrome aa3-600 menaquinol oxidase",
        "Cytochrome c oxidase, cbb3-type",
        "Cytochrome bd complex",
        "RuBisCo",
        "CBB Cycle",
        "rTCA Cycle",
        "Wood-Ljungdahl",
        "3-Hydroxypropionate Bicycle",
        "4-Hydroxybutyrate/3-hydroxypropionate",
        "pectinesterase",
        "diacetylchitobiose deacetylase",
        "glucoamylase",
        "D-galacturonate epimerase",
        "exo-poly-alpha-galacturonosidase",
        "oligogalacturonide lyase",
        "cellulase",
        "exopolygalacturonase",
        "chitinase",
        "basic endochitinase B",
        "bifunctional chitinase/lysozyme",
        "beta-N-acetylhexosaminidase",
        "D-galacturonate isomerase",
        "alpha-amylase",
        "beta-glucosidase",
        "pullulanase",
        "ammonia oxidation (amo/pmmo)",
        "hydroxylamine oxidation",
        "nitrite oxidation",
        "dissim nitrate reduction",
        "DNRA",
        "nitrite reduction",
        "nitric oxide reduction",
        "nitrous-oxide reduction",
        "nitrogen fixation",
        "hydrazine dehydrogenase",
        "hydrazine synthase",
        "dissimilatory sulfate < > APS",
        "dissimilatory sulfite < > APS",
        "dissimilatory sulfite < > sulfide",
        "thiosulfate oxidation",
        "alt thiosulfate oxidation tsdA",
        "alt thiosulfate oxidation doxAD",
        "sulfur reductase sreABC",
        "thiosulfate/polysulfide reductase",
        "sulfhydrogenase",
        "sulfur disproportionation",
        "sulfur dioxygenase",
        "sulfite dehydrogenase",
        "sulfite dehydrogenase (quinone)",
        "sulfide oxidation",
        "sulfur assimilation",
        "DMSP demethylation",
        "DMS dehydrogenase",
        "DMSO reductase",
        "NiFe hydrogenase",
        "ferredoxin hydrogenase",
        "membrane-bound hydrogenase",
        "hydrogen:quinone oxidoreductase",
        "NAD-reducing hydrogenase",
        "NADP-reducing hydrogenase",
        "NiFe hydrogenase Hyd-1",
        "thiamin biosynthesis",
        "riboflavin biosynthesis",
        "cobalamin biosynthesis",
        "transporter: vitamin B12",
        "transporter: thiamin",
        "transporter: urea",
        "transporter: phosphonate",
        "transporter: phosphate",
        "Flagellum",
        "Chemotaxis",
        "Methanogenesis via methanol",
        "Methanogenesis via acetate",
        "Methanogenesis via dimethylsulfide, methanethiol, methylpropanoate",
        "Methanogenesis via methylamine",
        "Methanogenesis via trimethylamine",
        "Methanogenesis via dimethylamine",
        "Methanogenesis via CO2",
        "Coenzyme B/Coenzyme M regeneration",
        "Coenzyme M reduction to methane",
        "Soluble methane monooxygenase",
        "methanol dehydrogenase",
        "alcohol oxidase",
        "dimethylamine/trimethylamine dehydrogenase",
        "Photosystem II",
        "Photosystem I",
        "Cytochrome b6/f complex",
        "anoxygenic type-II reaction center",
        "anoxygenic type-I reaction center",
        "Retinal biosynthesis",
        "Retinal from apo-carotenals",
        "Entner-Doudoroff Pathway",
        "Mixed acid: Lactate",
        "Mixed acid: Formate",
        "Mixed acid: Formate to CO2 & H2",
        "Mixed acid: Acetate",
        "Mixed acid: Ethanol, Acetate to Acetylaldehyde",
        "Mixed acid: Ethanol, Acetyl-CoA to Acetylaldehyde (reversible)",
        "Mixed acid: Ethanol, Acetylaldehyde to Ethanol",
        "Mixed acid: PEP to Succinate via OAA, malate & fumarate",
        "Naphthalene degradation to salicylate",
        "Biofilm PGA Synthesis protein",
        "Colanic acid and Biofilm transcriptional regulator",
        "Biofilm regulator BssS",
        "Colanic acid and Biofilm protein A",
        "Curli fimbriae biosynthesis",
        "Adhesion",
        "Competence-related core components",
        "Competence-related related components",
        "Competence factors",
        "Glyoxylate shunt",
        "Anaplerotic genes",
        "Sulfolipid biosynthesis",
        "C-P lyase cleavage PhnJ",
        "CP-lyase complex",
        "CP-lyase operon",
        "Type I Secretion",
        "Type III Secretion",
        "Type II Secretion",
        "Type IV Secretion",
        "Type VI Secretion",
        "Sec-SRP",
        "Twin Arginine Targeting",
        "Type Vabc Secretion",
        "Serine pathway/formaldehyde assimilation",
        "Arsenic reduction",
        "Cobalt transporter CbiMQ",
        "Cobalt transporter CbtA",
        "Cobalt transporter CorA",
        "Nickel ABC-type substrate-binding NikA",
        "Copper transporter CopA",
        "Ferrous iron transporter FeoB",
        "Ferric iron ABC-type substrate-binding AfuA",
        "Fe-Mn transporter MntH",
        "histidine",
        "arginine",
        "lysine",
        "serine",
        "threonine",
        "asparagine",
        "glutamine",
        "cysteine",
        "glycine",
        "proline",
        "alanine",
        "valine",
        "methionine",
        "phenylalanine",
        "isoleucine",
        "leucine",
        "tryptophan",
        "tyrosine",
        "aspartate",
        "glutamate",
        "PET degradation",
        "starch/glycogen synthesis",
        "starch/glycogen degradation",
        "polyhydroxybutyrate synthesis",
        "bidirectional polyphosphate",
        "carotenoids backbone biosynthesis",
        "end-product astaxanthin",
        "end-product nostoxanthin",
        "end-product zeaxanthin diglucoside",
        "end-product myxoxanthophylls",
        "staphyloaxanthin biosynthesis",
        "mevalonate pathway",
        "MEP-DOXP pathway",
    ]

    # Prepare output
    with open(args.output, "w") as out_file:
        out_file.write("Genome\t" + "\t".join(function_order) + "\n")
        for genome, ko_list in genome_data.items():
            # Generate pathway data for the genome
            pathway_data = {func: 0 for func in function_order}
            functions = [
                nitrogen,
                glycolysis,
                gluconeogenesis,
                tca_cycle,
                cbb_cycle,
                reverse_tca,
                wood_ljungdahl,
                three_prop,
                four_hydrox,
                c_degradation,
                chemotaxis,
                flagellum,
                sulfur,
                methanogenesis,
                methane_ox,
                hydrogen,
                transporters,
                riboflavin,
                thiamin,
                oxidative_phosphorylation,
                photosynthesis,
                entnerdoudoroff,
                mixedacid,
                naphthalene,
                biofilm,
                cobalamin,
                competence,
                anaplerotic,
                sulfolipid,
                cplyase,
                secretion,
                serine,
                arsenic,
                metal_transport,
                amino_acids,
                plastic,
                carbon_storage,
                phosphate_storage,
                carotenoids,
            ]
            for func in functions:
                pathway_data.update(func(ko_list))
                pathway_data = {
                    key: int(value) if isinstance(value, bool) else value
                    for key, value in pathway_data.items()
                }

            # Write results
            out_file.write(
                f"{genome}\t"
                + "\t".join(str(pathway_data[func]) for func in function_order)
                + "\n"
            )


if __name__ == "__main__":
    main()

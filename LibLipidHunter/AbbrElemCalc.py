# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2019  SysMedOs_team @ AG Bioanalytik, University of Leipzig:
# SysMedOs_team: Zhixu Ni, Georgia Angelidou, Mike Lange, Maria Fedorova
# LipidHunter is Dual-licensed
#     For academic and non-commercial use: `GPLv2 License` Please read more information by the following link:
#         [The GNU General Public License version 2] (https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
#     For commercial use:
#         please contact the SysMedOs_team by email.
# Please cite our publication in an appropriate form.
# Ni, Zhixu, Georgia Angelidou, Mike Lange, Ralf Hoffmann, and Maria Fedorova.
# "LipidHunter identifies phospholipids by high-throughput processing of LC-MS and shotgun lipidomics datasets."
# Analytical Chemistry (2017).
# DOI: 10.1021/acs.analchem.7b01126
#
# For more info please contact:
#     Developer Zhixu Ni zhixu.ni@uni-leipzig.de
#     Developer Georgia Angelidou georgia.angelidou@uni-leipzig.de

import re


class ElemCalc:
    def __init__(self):

        pa_hg_elem = {'C': 0, 'H': 3, 'O': 4, 'P': 1, 'N': 0, 'Na': 0}
        pl_elem_gen = {'C': 3, 'H': 2, 'O': 4, 'P': 0, 'N': 0, 'Na': 0}
        pc_hg_elem = {'C': 5, 'H': 14, 'O': 4, 'P': 1, 'N': 1, 'Na': 0}
        pe_hg_elem = {'C': 2, 'H': 8, 'O': 4, 'P': 1, 'N': 1, 'Na': 0}
        pg_hg_elem = {'C': 3, 'H': 9, 'O': 6, 'P': 1, 'N': 0, 'Na': 0}
        pi_hg_elem = {'C': 6, 'H': 13, 'O': 9, 'P': 1, 'N': 0, 'Na': 0}
        pip_hg_elem = {'C': 6, 'H': 14, 'O': 12, 'P': 2, 'N': 0, 'Na': 0}
        ps_hg_elem = {'C': 3, 'H': 8, 'O': 6, 'P': 1, 'N': 1, 'Na': 0}
        self.gen_hg_elem = {'C': 0, 'H': 0, 'O': 0, 'P': 0, 'N': 0, 'Na': 0} # General name for the different compounds such as TG, FA
        tg_elem_gen = {'C': 3, 'H': 2, 'O': 6, 'P': 0, 'N': 0, 'Na': 0}
        dg_elem_gen = {'C': 3, 'H': 4, 'O': 5, 'P': 0, 'N': 0, 'Na': 0}
        fa_elem_gen = {'C': 0, 'H': 0, 'O': 2, 'P': 0, 'N': 0, 'Na': 0}
        lpl_elem_gen = {'C': 3, 'H': 4, 'O': 3, 'P': 0, 'N': 0, 'Na': 0}
        cer_elem_gen = {'C': 0, 'H': 1, 'O': 1, 'P': 0, 'N': 1, 'Na': 0}

        # Note: Will be deleted (georgia: 14.2.2019)
        self.lipid_hg_elem_dct = {'PA': pa_hg_elem, 'PC': pc_hg_elem, 'PE': pe_hg_elem, 'PG': pg_hg_elem,
                                  'PI': pi_hg_elem, 'PS': ps_hg_elem, 'PIP': pip_hg_elem,
                                  'LPA': pa_hg_elem, 'LPC': pc_hg_elem, 'LPE': pe_hg_elem, 'LPG': pg_hg_elem,
                                  'LPI': pi_hg_elem, 'LPS': ps_hg_elem, 'LPIP': pip_hg_elem,
                                  'TG': self.gen_hg_elem,'FA': self.gen_hg_elem, 'DG': self.gen_hg_elem, 'Cer': self.gen_hg_elem, 'SM': pc_hg_elem}
        self.lipid_hg_elem_dct2 = {'PA': [pa_hg_elem, pl_elem_gen], 'PC': [pc_hg_elem, pl_elem_gen],
                                   'PE': [pe_hg_elem, pl_elem_gen], 'PG': [pg_hg_elem, pl_elem_gen],
                                  'PI': [pi_hg_elem, pl_elem_gen], 'PS': [ps_hg_elem, pl_elem_gen],
                                   'PIP': [pip_hg_elem, pl_elem_gen], 'LPA': [pa_hg_elem, lpl_elem_gen],
                                   'LPC': [pc_hg_elem, lpl_elem_gen], 'LPE': [pe_hg_elem, lpl_elem_gen],
                                   'LPG': [pg_hg_elem, lpl_elem_gen], 'LPI': [pi_hg_elem, lpl_elem_gen],
                                   'LPS': [ps_hg_elem, lpl_elem_gen], 'LPIP': [pip_hg_elem, lpl_elem_gen],
                                  'TG': [self.gen_hg_elem, tg_elem_gen], 'FA': [self.gen_hg_elem, fa_elem_gen],
                                   'DG': [self.gen_hg_elem, dg_elem_gen], 'Cer': [self.gen_hg_elem, cer_elem_gen]}

        self.glycerol_bone_elem_dct = {'C': 3, 'H': 2}
        # Note: will be deleted (georgia: 14.2.2019)
        # self.link_o_elem_dct = {'O': -1, 'H': 2}
        # self.link_p_elem_dct = {'O': -1}
        self.link_elem_dct = {'O-': {'O': -1, 'H': 2},
                              'P-': {'O': -1},
                              'm': {'O': 1, 'H':3, 'N':1},
                              'd': {'O': 2},
                              't': {'O':3}}

        self.periodic_table_dct = {'H': [(1.0078250321, 0.999885), (2.0141017780, 0.0001157)],
                                   'D': [(2.0141017780, 0.0001157)],
                                   'C': [(12.0, 0.9893), (13.0033548378, 0.0107)],
                                   'N': [(14.0030740052, 0.99632), (15.0001088984, 0.00368)],
                                   'O': [(15.9949146221, 0.99757), (16.99913150, 0.00038), (17.9991604, 0.00205)],
                                   'Na': [(22.98976967, 1.0)],
                                   'P': [(30.97376151, 1.0)],
                                   'S': [(31.97207069, 0.9493), (32.97145850, 0.0076),
                                         (33.96786683, 0.0429), (35.96708088, 0.0002)],
                                   'K': [(38.9637069, 0.932581), (39.96399867, 0.000117), (40.96182597, 0.067302)],
                                   }

        self.fa_rgx = re.compile(r'([a-zA-Z\-]{1,3})*(\()*(([a-zA-Z\-]{1,3})*(\d{1,2})(:)(\d)(;)*(\d)*)(\))*')

        fa_2_link_dct = {'A-': ['A-A-', {'A':''}],
                       'O-': ['O-A-', {'O':'', 'A':'O-'}],
                       'P-': ['P-A-', {'P':'', 'A':'P-'}]}
        fa_1_link_dct = {'A-': ['A-', {'A': ''}],
                       'O-': ['O-', {'O': ''}],
                       'P-': ['P-', {'P': ''}]}
        fa_3_link_dct = {'A-': ['A-A-A-', {'A': ''}],
                         'O-': ['O-A-A-', {'O': '', 'A':'O-'}],
                         'P-': ['P-A-A-', {'P': '', 'A':'P-'}]}
        self.lipid_link_dct = {'PL': fa_2_link_dct, 'PA': fa_2_link_dct, 'PC': fa_2_link_dct, 'PE': fa_2_link_dct,
                               'PG':fa_2_link_dct, 'PI': fa_2_link_dct, 'PIP':fa_2_link_dct, 'PS': fa_2_link_dct,
                               'LPL': fa_1_link_dct, 'LPA': fa_1_link_dct, 'LPC': fa_1_link_dct, 'LPE': fa_1_link_dct,
                               'LPG': fa_1_link_dct, 'LPI': fa_1_link_dct, 'LPIP': fa_1_link_dct, 'LPS': fa_1_link_dct,
                               'TG': fa_3_link_dct, 'DG': fa_2_link_dct, "Cer": ''}

        self.ion_mode_elem = {'[M-H]-': [{'H': -1}, '-'], '[M+FA-H]-': [{'H': 1, 'C': 1, 'O': 2}, '-'],
                              '[M+HCOO]-': [{'H': 1, 'C': 1, 'O': 2}, '-'],
                              '[M+CH3COO]-': [{'H': 3, 'C': 2, 'O': 2}, '-'],
                              '[M+OAc]-': [{'H': 3, 'C': 2, 'O': 2}, '-'], '[M+H]+': [{'H': 1}, '+'],
                              '[M+NH4]+': [{'N': 1, 'H': 4}, '+'], '[M+Na]+': [{'Na': 1}, '+'],
                              '[M+K]+': [{'K': 1}, '+'], '[M+H-H2O]+': [{'H': -1, 'O': -1}, '+'],
                              '[M+H-2xH2O]+': [{'H': -3, 'O': -2}, '+']}


    def decode_abbr(self, abbr):

        # Check PL Type
        _pl_typ = ''
        bulk_fa_typ = ''
        bulk_fa_linker = ''
        bulk_fa_c = 0
        bulk_fa_db = 0
        lyso_fa_linker_dct = {'fa1': '', 'fa2': ''}

        abbr_re_chk = self.fa_rgx.match(abbr)
        if abbr_re_chk :

            abbr_typ_lst = abbr_re_chk.groups()
            #print (abbr_typ_lst)
            if abbr_typ_lst[0] in [None, 'O-', 'P-', 'A-']:
                _pl_typ = 'FA'
            else:
                _pl_typ = abbr_typ_lst[0]
            bulk_fa_c = abbr_typ_lst[4]
            bulk_fa_db = abbr_typ_lst[6]
            if abbr_typ_lst[3] is None:
                # Comment: Not true in ceramides but cannot influence in the later steps so we leave it like this
                bulk_fa_linker = 'A-'
            else:
                bulk_fa_linker = abbr_typ_lst[3]
            if abbr_typ_lst[8] is not None:
                bulk_fa_o = abbr_typ_lst[8]
            else:
                bulk_fa_o = 0

        bulk_fa_c = int(bulk_fa_c)
        bulk_fa_db = int(bulk_fa_db)
        bulk_fa_o = int(bulk_fa_o)
        # Comment: bulk_fa_o should indicate the number of hydroxy groups (side chains) in the structure
        # Current use for the sphingolipids
        lipid_info_dct = {'TYPE': _pl_typ, 'LINK': bulk_fa_linker, 'C': bulk_fa_c, 'DB': bulk_fa_db, 'O': bulk_fa_o}

        return lipid_info_dct

    def get_neutral_elem(self, abbr):
        # FixMe: need to add for the ceramide bases (georgia: 20.2.2019)
        usr_lipid_info_dct = self.decode_abbr(abbr)

        lipid_type = usr_lipid_info_dct['TYPE']
        if lipid_type in self.lipid_hg_elem_dct2.keys():
            tmp_lipid_elem_dct = self.lipid_hg_elem_dct2[lipid_type][0].copy()
            for k in tmp_lipid_elem_dct.keys():
                tmp_lipid_elem_dct[k] += self.lipid_hg_elem_dct2[lipid_type][1][k]
            tmp_lipid_elem_dct['C'] += usr_lipid_info_dct['C']
            tmp_lipid_elem_dct['H'] += usr_lipid_info_dct['C'] * 2 - usr_lipid_info_dct['DB'] * 2
            tmp_lipid_elem_dct['O'] += usr_lipid_info_dct['O']
            if usr_lipid_info_dct['LINK'] in self.link_elem_dct.keys():
                for k in self.link_elem_dct[usr_lipid_info_dct['LINK']].keys():
                    tmp_lipid_elem_dct[k] += self.link_elem_dct[usr_lipid_info_dct['LINK']][k]

        else:
            tmp_lipid_elem_dct = self.gen_hg_elem
        return tmp_lipid_elem_dct

    def get_charged_elem(self, abbr, charge='[M-H]-'):

        lipid_elem_dct = self.get_neutral_elem(abbr)
        if charge in self.ion_mode_elem.keys():
            for k in self.ion_mode_elem[charge][0].keys():
                lipid_elem_dct[k] += self.ion_mode_elem[charge][0][k]

        return lipid_elem_dct

    def get_formula(self, abbr, charge=''):

        if charge in ['neutral', 'Neutral', '', None]:

            elem_dct = self.get_neutral_elem(abbr)
        else:
            elem_dct = self.get_charged_elem(abbr, charge=charge)

        formula_str = ''
        for k in elem_dct.keys():
            if elem_dct[k] == 1:
                formula_str += k
            elif elem_dct[k] > 1:
                formula_str += '{el}{el_n}'.format(el=k, el_n=elem_dct[k])
        if charge not in ['Neutral', 'neutral', '', None]:
            formula_str += self.ion_mode_elem[charge][1]

        return formula_str, elem_dct

    def get_exactmass(self, elem_dct):

        mono_mz = 0.0
        for _elem in list(elem_dct.keys()):
            mono_mz += elem_dct[_elem] * self.periodic_table_dct[_elem][0][0]

        return round(mono_mz, 6)

    # Function to calculate the possible precursor of [M+NH4]+ for TG and DG
    # Current step is working for TG
    # This is needed to understand if the precursors is true [M+H]+ or [M+Na]+ (given the users option)
    def get_NH3_pos_mode(self, charge, mz_pr, amm_elem_dct):
        mz_NH3_pr_H = ''  # The corespond mz of [M+NH4]+ if the given precursor corresponds to the [M+H]+
        mz_NH3_pr_Na = ''  # The corespond mz of [M+NH4]+ if the given precursor corresponds to the [M+Na]+
        if charge in ['[M+H]+']:
            # Problem need to calculate the theoritical one and not according to the experimental identification
            # mz_NH3_pr_H = mz_pr - self.periodic_table_dct['H'][0][0] + (4 * self.periodic_table_dct['H'][0][0]) + \
            #               self.periodic_table_dct['N'][0][0]
            mz_NH3_pr_H = amm_elem_dct['C'] * self.periodic_table_dct['C'][0][0] + amm_elem_dct['H'] * \
                          self.periodic_table_dct['H'][0][0] + amm_elem_dct['O'] * self.periodic_table_dct['O'][0][0] + \
                          self.periodic_table_dct['N'][0][0]
            # If this precursor corresponds to the [M+Na]+ then to calculate the bulk identification which it will be different from the above
            # We do the following calculations
            # First remove the charge and the atoms which form the glycerol bond (Na, C3, H5)
            # C3H5Na = 64.028895
            mz_pr_Na = mz_pr - self.periodic_table_dct['Na'][0][0] - (self.periodic_table_dct['C'][0][0] * 3) - (
                    self.periodic_table_dct['H'][0][0] * 5)
            # Second Step: For TG Remove the 6O and the first C from the 3 FA and the last C with the 3 H from each
            # O = 15.994915, C = 12, CH3 = 15.023475
            # 6O, 3xC, 3xCH3 => C6H9O6 = 177.039915
            mz_pr_Na = mz_pr_Na - (self.periodic_table_dct['O'][0][0] * 6) - (
                    self.periodic_table_dct['C'][0][0] * 6) - (self.periodic_table_dct['H'][0][0] * 9)
            mz_pr_Na = int(mz_pr_Na)
            db_count_Na = 0
            while (mz_pr_Na % 14 > 1):
                db_count_Na = db_count_Na + 1
                mz_pr_Na = mz_pr_Na - 26
            c_count_Na = int(mz_pr_Na / 14) + 6 + db_count_Na * 2
            tg_abbt_bulk_Na = 'TG(' + str(c_count_Na) + ':' + str(db_count_Na) + ')'
            _mz_Na_formula, _mz_Na_elemdct = self.get_formula(tg_abbt_bulk_Na, '[M+Na]+')
            mz_NH3_pr_Na = _mz_Na_elemdct['C'] * self.periodic_table_dct['C'][0][0] + (
                    (_mz_Na_elemdct['H'] + 4) * self.periodic_table_dct['H'][0][0]) + _mz_Na_elemdct['O'] * \
                           self.periodic_table_dct['O'][0][0] + self.periodic_table_dct['N'][0][0]
            # Third step: the rest of the elements correspond to the CH2 * x and if DB to the (CHx2) * y (For 1DB == 2xCH)
            # CH2 = 14.015650, CH = 13.007825
            # Need to create a loop and make all the numbers integers
            # elif charge in ['[M+Na]+']:
            #     mz_NH3_pr_Na = mz_pr - self.periodic_table_dct['Na'][0][0] + (4 * self.periodic_table_dct['H'][0][0]) + \
            #                    self.periodic_table_dct['N'][0][0]

            # TODO(georgia.angelidou@uni-leipzig.de): _mz_H_formula is used before ref, fix here!
            # Temp add

            mz_NH4_H_form = 'C' + str(amm_elem_dct['C']) + 'H' + str(amm_elem_dct['H']) + 'O6N'

            # mz_NH4_Na_form = _mz_H_formula
            mz_NH4_Na_form = 'C' + str(_mz_Na_elemdct['C']) + 'H' + str((_mz_Na_elemdct['H'] + 3)) + 'O6N'

        elif charge in ['[M+Na]+']:
            mz_NH3_pr_Na = amm_elem_dct['C'] * self.periodic_table_dct['C'][0][0] + amm_elem_dct['H'] * \
                           self.periodic_table_dct['H'][0][0] + amm_elem_dct['O'] * self.periodic_table_dct['O'][0][0] + \
                           self.periodic_table_dct['N'][0][0]
            #print (mz_pr)
            C5H3= self.periodic_table_dct['H'][0][0] * 6  + self.periodic_table_dct['C'][0][0] *3
            rest_sampl = self.periodic_table_dct['O'][0][0] *6 + self.periodic_table_dct['H'][0][0] *9 + self.periodic_table_dct['C'][0][0] * 6
            mz_pr_H = mz_pr - C5H3 - rest_sampl
            mz_pr_H = int(mz_pr_H)
            db_count_H = 0
            while (mz_pr_H % 14 > 1):
                db_count_H = db_count_H + 1
                mz_pr_H = mz_pr_H - 26
            c_count_H = int(mz_pr_H / 14) + 6 + db_count_H * 2
            tg_abbt_bulk_H = 'TG(' + str(c_count_H) + ':' + str(db_count_H) + ')'
            _mz_H_formula, _mz_H_elemdct = self.get_formula(tg_abbt_bulk_H, '[M+H]+')
            mz_NH3_pr_H = _mz_H_elemdct['C'] * self.periodic_table_dct['C'][0][0] + (_mz_H_elemdct['H'] + 3) * \
                          self.periodic_table_dct['H'][0][0] + _mz_H_elemdct['O'] * self.periodic_table_dct['O'][0][0] + self.periodic_table_dct['N'][0][0]
            mz_NH4_Na_form = 'C' + str(amm_elem_dct['C']) + 'H' + str(amm_elem_dct['H']) + 'O6N'
            mz_NH4_H_form = 'C' + str(_mz_H_elemdct['C']) + 'H' + str((_mz_H_elemdct['H'] + 3)) + 'O6N'



        return (mz_NH3_pr_H, mz_NH4_H_form, mz_NH3_pr_Na, mz_NH4_Na_form)


if __name__ == '__main__':

    usr_bulk_abbr_lst = [
        # 'TG(48:2)',
        # 'PC(O-34:0)',
        #  'PC(36:3)',
        # 'TG(P-48:2)',
        # 'LPC(20:3)',
        # '35:3'
        # 'Cer(d34:0)',
        #'t10:0',
        # 'FA10:0'
        'Cer(30:1;2)'
    ]
    # charge_lst = ['[M+NH4]+', '[M-H]-', '[M+HCOO]-', '[M+OAc]-']
    # usr_bulk_abbr_lst = ['PC(36:3)', 'PC(O-36:3)', 'PC(P-36:3)']
    # charge_lst = ['', '[M-H]-', '[M+HCOO]-', '[M+OAc]-']
    charge_lst = ['', '[M+H]+', '[M-H]-']

    abbr2formula = ElemCalc()

    for usr_abbr in usr_bulk_abbr_lst:
        for _charge in charge_lst:
            usr_formula, usr_elem_dct = abbr2formula.get_formula(usr_abbr, charge=_charge)
            print((usr_abbr, _charge))
            print(usr_elem_dct)
            print(usr_formula)

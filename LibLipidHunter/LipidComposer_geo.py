# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2017  SysMedOs_team @ AG Bioanalytik, University of Leipzig:
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
#     SysMedOs_team: oxlpp@bbz.uni-leipzig.de
#     Developer Zhixu Ni zhixu.ni@uni-leipzig.de
#     Developer Georgia Angelidou georgia.angelidou@uni-leipzig.de

from __future__ import division
from __future__ import print_function

import itertools

import pandas as pd
import numpy as np
from natsort import natsorted, ns

try:
    from LibLipidHunter.LipidNomenclature import NameParserFA
    from LibLipidHunter.AbbrElemCalc import ElemCalc
    from LibLipidHunter.ParallelFunc import ppm_window_para
except ImportError:  # for python 2.7.14
    from LipidNomenclature import NameParserFA
    from AbbrElemCalc import ElemCalc
    from ParallelFunc import ppm_window_para


class LipidComposer:

    def __init__(self):
        # Note: ca be replace and use the one from ASbbrElemCalc. (georgia: 23.1.2019)
        # Delet: will be deleted (georgia: 23.1.2019)
        # pa_hg_elem = {'C': 0, 'H': 3, 'O': 4, 'P': 1, 'N': 0}
        # pc_hg_elem = {'C': 5, 'H': 14, 'O': 4, 'P': 1, 'N': 1}
        # pe_hg_elem = {'C': 2, 'H': 8, 'O': 4, 'P': 1, 'N': 1}
        # pg_hg_elem = {'C': 3, 'H': 9, 'O': 6, 'P': 1, 'N': 0}
        # pi_hg_elem = {'C': 6, 'H': 13, 'O': 9, 'P': 1, 'N': 0}
        # pip_hg_elem = {'C': 6, 'H': 14, 'O': 12, 'P': 2, 'N': 0}
        # ps_hg_elem = {'C': 3, 'H': 8, 'O': 6, 'P': 1, 'N': 1}
        # tg_hg_elem = {'C': 0, 'H': 0, 'O': 0, 'P': 0, 'N': 0}

        # Question: For what this is used. Remember to check it out (georgia: 23.1.2019)
        self.lipid_hg_lst = ['PA', 'PC', 'PE', 'PG', 'PI', 'PS', 'PIP', 'TG']

        self.lipid_hg_elem_dct = ElemCalc().lipid_hg_elem_dct
        # Note: will be replace by the one in the AbbrElemCalc. (georgia: 23.1.2019)
        # self.lipid_hg_elem_dct = {'PA': pa_hg_elem, 'PC': pc_hg_elem, 'PE': pe_hg_elem, 'PG': pg_hg_elem,
        #                           'PI': pi_hg_elem, 'PS': ps_hg_elem, 'PIP': pip_hg_elem, 'TG': tg_hg_elem,
        #                           'DG': tg_hg_elem}

        # Note: Already define in the AbbrElemCalc. Will be replace (georgia: 14.2.2019)
        self.glycerol_bone_elem_dct = ElemCalc().glycerol_bone_elem_dct
        self.link_o_elem_dct = {'O': -1, 'H': 2}
        self.link_p_elem_dct = {'O': -1}

        self.elem_dct = NameParserFA().elem_dct
        # Note: can be replace and just use directly the one form NameParserFA. (georgia: 23.1.2019)
        # self.elem_dct = {'H': [1.0078250321, 0.999885],
        #                  'D': [2.0141017780, 0.0001157],
        #                  'C': [12.0, 0.9893],
        #                  'N': [14.0030740052, 0.99632],
        #                  'O': [15.9949146221, 0.99757],
        #                  'Na': [22.98976967, 1.0],
        #                  'P': [30.97376151, 1.0],
        #                  'S': [31.97207069, 0.9493],
        #                  'K': [38.9637069, 0.932581]}

        # Note: need for 2 different functions (georgia: 23.1.2019)
        self.all_lipid_class_list = ['PL', 'PA', 'PC', 'PE', 'PG', 'PI', 'PS', 'SM', 'LPL', 'LPA', 'LPC', 'LPE', 'LPG',
                                'LPI', 'LPS', 'TG', 'DG', 'Cer']



    def calc_fa_df2(self, lipid_class, fa_df):
        # This function creates a list for all the different FA for the different position
        # Will be use in a later step to get all the possible structures that can be combine
        sn_units_lst = []
        # Note: the calc_fa_df was compine in this function (georgia: 15.2.2019)
        header_lst = fa_df.columns.values.tolist()
        print (NameParserFA(lipid_class).lipid_fa_dct[lipid_class])
        if NameParserFA(lipid_class).lipid_fa_dct[lipid_class][0] in header_lst and 'FATTYACID' in header_lst:
            # Note:  if statement will be remove
            if NameParserFA(lipid_class).lipid_fa_dct[lipid_class][2] == 'Base':
                base_lst=[]
                for k in NameParserFA(lipid_class).lipid_fa_dct[lipid_class][3]:
                    q_str = '{cl} == "T" and {fa} == "T"'.format(cl=NameParserFA().lipid_fa_dct[lipid_class][0], fa=k)
                    fa_lst = fa_df.query(q_str)['FATTYACID'].tolist()
                    fa_l_st = '_'.join(fa_lst)
                    fa_l_st = fa_l_st.replace('FA', k.lower())
                    fa_lst = fa_l_st.split('_')
                    base_lst = base_lst + fa_lst
                sn_units_lst.append(base_lst)
            for k in NameParserFA(lipid_class).lipid_fa_dct[lipid_class][1]:
                q_str = '{cl} == "T" and {fa} == "T"'.format(cl=NameParserFA(lipid_class).lipid_fa_dct[lipid_class][0], fa=k)
                print(q_str)
                fa_lst = fa_df.query(q_str)['FATTYACID'].tolist()
                spb_str = 'SPB'
                spb_lst = list(filter(lambda x: spb_str in x, fa_lst))
                if len(spb_lst) > 1:
                    sn_units_lst.append(spb_lst)
                    fa_str = 'FA'
                    fa_lst = list(filter(lambda x: fa_str in x, fa_lst))
                sn_units_lst.append(fa_lst)
            # # Note: it can be skip and do this in a later step (georgia: 18.2.2019)
            # if NameParserFA().lipid_fa_dct[lipid_class][0] == 'LPL':
            #     sn_units_lst.append('')

        return sn_units_lst
    # Note can be replace with the above (georgia: 15.2.2019)
    # @staticmethod
    # def calc_fa_df(lipid_class, fa_df):
    #     # This function creates a list for all the different FA for the different position
    #     # Will be use in a later step to get all the possible structures that can be combine
    #     sn_units_lst = []
    #
    #     header_lst = fa_df.columns.values.tolist()
    #     # Done (georgia): Reduce unneccessary memory by compiine the 2 steps in one 9.01019
    #     # Re-arrange: continue: pl_fa1_df = fa_df.query('PL == "T" and FA1 == "T"') ->
    #     # Re-arrange: continue: pl_fa1_lst = fa_df.query('PL == "T" and FA1 == "T"')['FATTYACID'].TOLIST()
    #     if lipid_class in ['PA', 'PC', 'PE', 'PG', 'PI', 'PS']:
    #         if 'PL' in header_lst and 'FATTYACID' in header_lst:
    #             pl_fa1_lst = fa_df.query('PL == "T" and FA1 == "T"')['FATTYACID'].tolist()
    #             pl_fa2_lst = fa_df.query('PL == "T" and FA2 == "T"')['FATTYACID'].tolist()
    #
    #             sn_units_lst = [pl_fa1_lst, pl_fa2_lst]
    #
    #     elif lipid_class in ['LPA', 'LPC', 'LPE', 'LPG', 'LPI', 'LPS']:
    #         # Note: we should include only one of the 2 but not both
    #         if 'LPL' in header_lst and 'FATTYACID' in header_lst:
    #             pl_fa1_lst = fa_df.query('LPL == "T" and FA1 == "T"')['FATTYACID'].tolist()
    #             # Empty list is need for the generation of the dataframe in later step
    #             sn_units_lst = [pl_fa1_lst, ['']]
    #         elif 'PL' in header_lst and 'FATTYACID' in header_lst:
    #             pl_fa1_lst = fa_df.query('PL == "T" and FA1 == "T"')['FATTYACID'].tolist()
    #             # Empty list is need for the generation of the dataframe in later step
    #             sn_units_lst = [pl_fa1_lst, ['']]
    #
    #     elif lipid_class in ['TG']:
    #         if 'TG' in header_lst and 'FATTYACID' in header_lst:
    #             tg_fa1_lst = fa_df.query('TG == "T" and FA1 == "T"')['FATTYACID'].tolist()
    #             tg_fa2_lst = fa_df.query('TG == "T" and FA2 == "T"')['FATTYACID'].tolist()
    #             tg_fa3_lst = fa_df.query('TG == "T" and FA3 == "T"')['FATTYACID'].tolist()
    #
    #             sn_units_lst = [tg_fa1_lst, tg_fa2_lst, tg_fa3_lst]
    #     elif lipid_class in ['DG']:
    #         if 'DG' in header_lst and 'FATTYACID' in header_lst:
    #             dg_fa1_lst = fa_df.query('TG == "T" and FA1 == "T"')['FATTYACID'].tolist()
    #             dg_fa2_lst = fa_df.query('TG == "T" and FA2 == "T"')['FATTYACID'].tolist()
    #
    #             sn_units_lst = [dg_fa1_lst, dg_fa2_lst]
    #     elif lipid_class in ['CL']:
    #         if 'CL' in header_lst and 'FATTYACID' in header_lst:
    #             cl_fa1_lst = fa_df.query('CL == "T" and FA1 == "T"')['FATTYACID'].tolist()
    #             cl_fa2_lst = fa_df.query('CL == "T" and FA2 == "T"')['FATTYACID'].tolist()
    #             cl_fa3_lst = fa_df.query('CL == "T" and FA3 == "T"')['FATTYACID'].tolist()
    #             cl_fa4_lst = fa_df.query('CL == "T" and FA4 == "T"')['FATTYACID'].tolist()
    #
    #             sn_units_lst = [cl_fa1_lst, cl_fa2_lst, cl_fa3_lst, cl_fa4_lst]
    #     elif lipid_class in ['Cer']:
    #         if 'CER' in header_lst and 'FATTYACID' in header_lst:
    #             cer_fa1_lst = fa_df.query('CER == "T" and FA1 == "T"')['FATTYACID'].tolist()
    #             cer_base_lst = ["d" + val_fa.strip('FA') for val_fa in fa_df.query('D == "T"')['FATTYACID'].tolist()]
    #
    #             sn_units_lst = [cer_base_lst, cer_fa1_lst]
    #
    #     return sn_units_lst

    # Creates all the fragments which have 1 FA or the free FA fragments + the query that will be used later in the MS2
    # to search if these fragments are present or not
    def calc_fa_query(self, lipid_class, ion_mode, fa_whitelist, ms2_ppm=100):

        usr_fa_df = pd.read_excel(fa_whitelist)
        usr_fa_df = usr_fa_df.fillna(value='F')
        tmp_columns = usr_fa_df.columns.tolist()

        usr_fa_df.columns = usr_fa_df.columns.str.upper()

        # COMPINE (georgia):  the below section was rearrange to one 23.01.19
        #  Note: is more like a control check (georgia:23.1.2019)
        if lipid_class in self.all_lipid_class_list:
            if lipid_class in tmp_columns:
                pass
            elif 'PL' in tmp_columns or 'LPL' in tmp_columns:
                pass
            else:
                return False
        else:
            return False

        #if lipid_class in ['PL', 'PA', 'PC', 'PE', 'PG', 'PI', 'PS', 'SM']:
        #     if lipid_class in tmp_columns:
        #         pass
        #     elif 'PL' in tmp_columns:
        #         pass
        #     else:
        #         return False
        # elif lipid_class in ['LPL', 'LPA', 'LPC', 'LPE', 'LPG', 'LPI', 'LPS']:
        #     if lipid_class in tmp_columns:
        #         pass
        #     elif 'LPL' in tmp_columns or 'PL' in tmp_columns:
        #         pass
        #     else:
        #         return False
        # elif lipid_class in ['TG', 'DG']:
        #     if lipid_class in tmp_columns:
        #         pass
        #     else:
        #         return False
        # else:
        #     return False

        sn_units_lst = self.calc_fa_df2(lipid_class, usr_fa_df)  # Return a list with list of the FA for each sn position
        fa_abbr_lst = []
        # For PL lem(sn_units_lst) = 2 and for TG len(sn_units_lst) = 3
        for _s in sn_units_lst:
            fa_abbr_lst.extend(_s)  # Put all the FA in one list
        fa_abbr_lst = sorted(list(set(fa_abbr_lst)))

        abbr_parser = NameParserFA(lipid_class)
        elem_calc = ElemCalc()
        usr_fa_dct = {}
        for _fa_abbr in fa_abbr_lst:
            if _fa_abbr:
                _fa_info_dct = abbr_parser.get_fa_info_geo(_fa_abbr, lipid_class, ion_mode)  # Calculate all the information for each FA
                # Note: we do not need it since the reason that it is used is unecessary know (georgia: 21.2.2019)
                # _lipid_formula, _lipid_elem_dct = elem_calc.get_formula(_fa_abbr)  # get the elemental composition of FA

                # delet: the below lines will be deleted. The information are already inside the dict (georgia:23.1.2019)
                # add the Abbr, formula and the exact mass in the dictionary
                # _fa_info_dct['ABBR'] = _fa_abbr
                # _fa_info_dct['FORMULA'] = _lipid_formula
                # _fa_info_dct['EXACTMASS'] = elem_calc.get_exactmass(_lipid_elem_dct)  # Calc. the exact mass for each FA
                usr_fa_dct[_fa_abbr] = _fa_info_dct

        usr_fa_df = pd.DataFrame(usr_fa_dct).T.copy()  # put all the info for the FA in a dataframe
        usr_fa_df.is_copy = False

        # Note: move to a previous section inside get_fa_info_geo (georgia: 24.1.2019)
        # create the queries for the FA fragments and MG
        # for _fa_ion in ['[FA-H]-', '[FA-H2O-H]-', '[FA-H2O+H]+']:
        #     usr_fa_df['%s_MZ_LOW' % _fa_ion] = ppm_window_para(usr_fa_df['%s_MZ' % _fa_ion].values.tolist(),
        #                                                        ms2_ppm * -1)
        #     usr_fa_df['%s_MZ_HIGH' % _fa_ion] = ppm_window_para(usr_fa_df['%s_MZ' % _fa_ion].values.tolist(), ms2_ppm)
        #     usr_fa_df['%s_Q' % _fa_ion] = (usr_fa_df['%s_MZ_LOW' % _fa_ion].astype(str) + ' <= mz <= '
        #                                    + usr_fa_df['%s_MZ_HIGH' % _fa_ion].astype(str))

        # More specific fragments for PL
        if lipid_class in ['PA', 'PC', 'PE', 'PG', 'PI', 'PS', 'PIP']:
            pass
            # Note: all of this section now is located inside the LipidNomenclature.py in the function frag_definition (georgia:24.1.2019)
            # # there alreadz the backbone of the stucture eg. for PE C5H10NO4P
            # # for the [LPE(16:0)-H]- missing the exact mass of the FA
            # # for the [LPE(16:0)-H2O-H]- we have the loss of water which already calculated in the structure
            # # thats why addition of the FA but without of the water
            # lyso_type_dct = {'[L%s-H]-' % lipid_class: 'EXACTMASS', '[L%s-H2O-H]-' % lipid_class: '[FA-H2O]_MZ'}
            #
            # # backbone creation for the different PL
            # lyso_base_elem_dct = self.lipid_hg_elem_dct[lipid_class]
            # for _e in list(self.glycerol_bone_elem_dct.keys()):
            #     lyso_base_elem_dct[_e] += self.glycerol_bone_elem_dct[_e]
            #
            # # the element here is with no Hydroxyl on fa1 and fa2, here a [M-H]- is already considered
            # lyso_base_mz = elem_calc.get_exactmass(lyso_base_elem_dct) + 1.0078250321 + 15.9949146221
            #
            # if lipid_class in ['PC', 'SM']:
            #     lyso_base_mz -= (12.0 + 2 * 1.0078250321)  # LPC loss one -CH3 from HG (one H already remove above)
            #
            # for _lyso_ion in list(lyso_type_dct.keys()):
            #     if lipid_class in ['PC']:
            #         if lyso_type_dct[_lyso_ion] == 'EXACTMASS':
            #             usr_fa_df['%s_ABBR' % _lyso_ion] = ('[L' + lipid_class + '(' + usr_fa_df['ABBR'].str.strip('FA')
            #                                                 + ')-CH3]-')
            #         elif lyso_type_dct[_lyso_ion] == '[FA-H2O]_MZ':
            #             usr_fa_df['%s_ABBR' % _lyso_ion] = ('[L' + lipid_class + '(' + usr_fa_df['ABBR'].str.strip('FA')
            #                                                 + ')-H2O-CH3]-')
            #         else:
            #             usr_fa_df['%s_ABBR' % _lyso_ion] = 'ERROR'
            #     else:
            #         if lyso_type_dct[_lyso_ion] == 'EXACTMASS':
            #             usr_fa_df['%s_ABBR' % _lyso_ion] = ('[L' + lipid_class + '(' + usr_fa_df['ABBR'].str.strip('FA')
            #                                                 + ')-H]-')
            #         elif lyso_type_dct[_lyso_ion] == '[FA-H2O]_MZ':
            #             usr_fa_df['%s_ABBR' % _lyso_ion] = ('[L' + lipid_class + '(' + usr_fa_df['ABBR'].str.strip('FA')
            #                                                 + ')-H2O-H]-')
            #         else:
            #             usr_fa_df['%s_ABBR' % _lyso_ion] = 'ERROR'
            #
            #     usr_fa_df['%s_MZ' % _lyso_ion] = lyso_base_mz + usr_fa_df[lyso_type_dct[_lyso_ion]]
            #     usr_fa_df['%s_MZ_LOW' % _lyso_ion] = ppm_window_para(usr_fa_df['%s_MZ' % _lyso_ion].values.tolist(),
            #                                                          ms2_ppm * -1)
            #     usr_fa_df['%s_MZ_HIGH' % _lyso_ion] = ppm_window_para(usr_fa_df['%s_MZ' % _lyso_ion].values.tolist(),
            #                                                           ms2_ppm)
            #     usr_fa_df['%s_Q' % _lyso_ion] = (usr_fa_df['%s_MZ_LOW' % _lyso_ion].astype(str) + ' <= mz <= '
            #                                      + usr_fa_df['%s_MZ_HIGH' % _lyso_ion].astype(str))
        elif lipid_class in ['TG']:
            pass
            # Note: all of this section now is located inside the LipidNomenclature.py in the function frag_definition (georgia:13.2.2019)
            # Cannot calculate the theoritical m/z values of the DG fragments sinc we calculate the loss of a FA
            # and we dont know the cobination of the remaining 2

            # mg_type_dct = {'[MG-H2O+H]+': 'EXACTMASS'}
            # mg_base_elem_dct = self.lipid_hg_elem_dct[lipid_class]
            #
            # for _e in self.glycerol_bone_elem_dct.keys():
            #     mg_base_elem_dct[_e] += self.glycerol_bone_elem_dct[_e]
            #
            # # Calculate the rest of monoglycerol after the neutral loss of 2 FA in protonated form (one without Water)
            # mg_base_elem_dct = elem_calc.get_exactmass(mg_base_elem_dct) + 15.9949146221 + (3 * 1.0078250321)
            # for _mg_ion in mg_type_dct.keys():
            #     usr_fa_df['%s_ABBR' % _mg_ion] = ('[MG(' + usr_fa_df['ABBR'].str.strip('FA') + ')-H2O+H]+')
            #     usr_fa_df['%s_MZ' % _mg_ion] = mg_base_elem_dct + usr_fa_df[mg_type_dct[_mg_ion]]
            #     usr_fa_df['%s_MZ_LOW' % _mg_ion] = ppm_window_para(usr_fa_df['%s_MZ' % _mg_ion].values.tolist(),
            #                                                        ms2_ppm * -1)
            #     usr_fa_df['%s_MZ_HIGH' % _mg_ion] = ppm_window_para(usr_fa_df['%s_MZ' % _mg_ion].values.tolist(),
            #                                                         ms2_ppm)
            #     usr_fa_df['%s_Q' % _mg_ion] = (usr_fa_df['%s_MZ_LOW' % _mg_ion].astype(str) + ' <= mz <= ' + usr_fa_df[
            #         '%s_MZ_HIGH' % _mg_ion].astype(str))
        elif lipid_class in ['DG']:
            pass
            # Note: all of this section now is located inside the LipidNomenclature.py in the function frag_definition (georgia:13.2.2019)
            # mg_type_dct = {'[MG-H2O+H]+': 'EXACTMASS'}
            # mg_base_elem_dct = self.lipid_hg_elem_dct[lipid_class]
            #
            # for _e in self.glycerol_bone_elem_dct.keys():
            #     mg_base_elem_dct[_e] += self.glycerol_bone_elem_dct[_e]
            #
            # # Calculate the rest of monoglycerol after the neutral loss of 2 FA in protonated form (one without Water)
            # mg_base_elem_dct = elem_calc.get_exactmass(mg_base_elem_dct) + 15.9949146221 + (3 * 1.0078250321)
            # for _mg_ion in mg_type_dct.keys():
            #     usr_fa_df['%s_ABBR' % _mg_ion] = ('[MG(' + usr_fa_df['ABBR'].str.strip('FA') + ')-H2O+H]+')
            #     usr_fa_df['%s_MZ' % _mg_ion] = mg_base_elem_dct + usr_fa_df[mg_type_dct[_mg_ion]]
            #     usr_fa_df['%s_MZ_LOW' % _mg_ion] = ppm_window_para(usr_fa_df['%s_MZ' % _mg_ion].values.tolist(),
            #                                                        ms2_ppm * -1)
            #     usr_fa_df['%s_MZ_HIGH' % _mg_ion] = ppm_window_para(usr_fa_df['%s_MZ' % _mg_ion].values.tolist(),
            #                                                         ms2_ppm)
            #     usr_fa_df['%s_Q' % _mg_ion] = (usr_fa_df['%s_MZ_LOW' % _mg_ion].astype(str) + ' <= mz <= ' + usr_fa_df[
            #         '%s_MZ_HIGH' % _mg_ion].astype(str))
        else:
            # TODO (georgia.angelidou@uni-leipzig.de): SM
            pass
        return usr_fa_df

    def gen_all_comb(self, lipid_class, usr_fa_df, position=False):


        fa_units_lst = self.calc_fa_df2(lipid_class, usr_fa_df)

        if NameParserFA(lipid_class).lipid_fa_dct[lipid_class][4] == 1:
            fa_comb_lst = list(itertools.product(fa_units_lst[0], ['']))
            fa_df_header_lst = NameParserFA(lipid_class).lipid_fa_dct[lipid_class][1]
            fa_df_header_lst.append('FA2')
        elif NameParserFA(lipid_class).lipid_fa_dct[lipid_class][4] == 2:
            fa_comb_lst = list(itertools.product(fa_units_lst[0], fa_units_lst[1]))
            fa_df_header_lst = NameParserFA(lipid_class).lipid_fa_dct[lipid_class][1]
            # if lipid_class == 'Cer':
            #     fa_df_header_lst = [NameParserFA().lipid_fa_dct[lipid_class][2]] + fa_df_header_lst
        elif NameParserFA(lipid_class).lipid_fa_dct[lipid_class][4] == 3:
            fa_comb_lst = list(itertools.product(fa_units_lst[0], fa_units_lst[1], fa_units_lst[2]))
            fa_df_header_lst = NameParserFA(lipid_class).lipid_fa_dct[lipid_class][1]
        elif NameParserFA(lipid_class).lipid_fa_dct[lipid_class][4] == 4:
            fa_comb_lst = list(itertools.product(fa_units_lst[0], fa_units_lst[1], fa_units_lst[2], fa_units_lst[3]))
            fa_df_header_lst = NameParserFA(lipid_class).lipid_fa_dct[lipid_class][1]
        else:
            fa_comb_lst = []
            fa_df_header_lst = []



        # Note: the below section was combine to the above one (georgia: 18.2.2019)
        # if lipid_class in ['PA', 'PC', 'PE', 'PG', 'PI', 'PS', 'DG', 'SM'] and len(fa_units_lst) == 2:
        #     fa_comb_lst = list(itertools.product(fa_units_lst[0], fa_units_lst[1]))
        #     fa_df_header_lst = ['FA1', 'FA2']
        #     # lipid_template = '{}'
        # elif lipid_class in ['LPA', 'LPC', 'LPE', 'LPG', 'LPI', 'LPS'] and len(fa_units_lst) == 2:
        #     fa_comb_lst = list(itertools.product(fa_units_lst[0], fa_units_lst[1]))
        #     # FA2 need for the generation of the dataframe in later step. Does not contain any information
        #     fa_df_header_lst = ['FA1', 'FA2']
        #     # lipid_template = '{}'
        # elif lipid_class == 'TG' and len(fa_units_lst) == 3:
        #     fa_comb_lst = list(itertools.product(fa_units_lst[0], fa_units_lst[1], fa_units_lst[2]))
        #     fa_df_header_lst = ['FA1', 'FA2', 'FA3']
        # elif lipid_class == 'CL' and len(fa_units_lst) == 4:
        #     fa_comb_lst = list(itertools.product(fa_units_lst[0], fa_units_lst[1], fa_units_lst[2], fa_units_lst[3]))
        #     fa_df_header_lst = ['FA1', 'FA2', 'FA3', 'FA4']
        # elif lipid_class == 'Cer' and len(fa_units_lst) == 2:
        #     fa_comb_lst = list(itertools.product(fa_units_lst[0], fa_units_lst[1]))
        #     fa_df_header_lst = ['Base', 'FA1']
        # else:
        #     fa_comb_lst = []
        #     fa_df_header_lst = []



        fa_combo_df = pd.DataFrame(data=fa_comb_lst, columns=fa_df_header_lst)

        fa_combo_df['CLASS'] = lipid_class

        # Note: a new way to combine the below section (georgia: 19.2.019)
        if 'Base' in fa_df_header_lst:
            fa_link_df = fa_combo_df
            fa_link_df.is_copy = False
            fa_link_df['DISCRETE_ABBR'] = (fa_link_df['CLASS'] + '(' + fa_link_df[fa_df_header_lst[0]] + '_' +
                                           fa_link_df[fa_df_header_lst[1]].str.strip('FA)') + ')')
            fa_link_df.sort_values(by='DISCRETE_ABBR', inplace=True)
            fa_combo_df = fa_link_df
            print ('[INFO] --> Number of predicted lipids (exact position): ', fa_combo_df.shape[0])
        else:
            fa_combo_link_df = fa_combo_df
            fa_combo_link_df.is_copy = False
            fa_combo_link_df['LINK'] = fa_combo_link_df['FA1'].str[0:2]
            fa_link_df = fa_combo_link_df[(fa_combo_link_df['LINK'] == "FA") | (fa_combo_link_df['LINK'] == "SP")]
            fa_link_df.is_copy = False
            fa_link_df.drop(['LINK', 'CLASS'], axis=1, inplace=True)
            if NameParserFA(lipid_class).lipid_fa_dct[lipid_class][2] != 0:
                fa_link_df.values.sort(kind='mergesort')
            fa_link_df['CLASS'] = lipid_class
            # Note: The header list is never len 1
            if len(fa_df_header_lst) == 1:
                fa_link_df['DISCRETE_ABBR'] = (fa_link_df['CLASS'] + '(' +
                                            fa_link_df[fa_df_header_lst[0]].str.strip('FA').str.strip('SPB') + ')')
            elif len(fa_df_header_lst) == 2:
                fa_link_df['DISCRETE_ABBR'] = (fa_link_df['CLASS'] + '(' +
                                               fa_link_df[fa_df_header_lst[0]].str.strip('FA').str.strip('SPB') + '_' +
                                               fa_link_df[fa_df_header_lst[1]].str.strip('FA') + ')')
                if NameParserFA(lipid_class).lipid_fa_dct[lipid_class][4] == 1:
                    fa_link_df['DISCRETE_ABBR'] = fa_link_df['DISCRETE_ABBR'].str.replace(r'_', '')
            elif len(fa_df_header_lst) == 3:
                fa_link_df['DISCRETE_ABBR'] = (fa_link_df['CLASS'] + '(' +
                                               fa_link_df[fa_df_header_lst[0]].str.strip('FA') + '_' +
                                               fa_link_df[fa_df_header_lst[1]].str.strip('FA') + '_' +
                                               fa_link_df[fa_df_header_lst[2]].str.strip('FA') + ')')
            elif len(fa_df_header_lst) == 4:
                fa_combo_df['DISCRETE_ABBR'] = (fa_combo_df['CLASS'] + '(' +
                                                fa_combo_df[fa_df_header_lst[0]].str.strip('FA') + '_' +
                                                fa_combo_df[fa_df_header_lst[1]].str.strip('FA') + '_' +
                                                fa_combo_df[fa_df_header_lst[2]].str.strip('FA') + '_' +
                                                fa_combo_df[fa_df_header_lst[3]].str.strip('FA') + ')')

            if NameParserFA(lipid_class).lipid_fa_dct[lipid_class][5]:
                op_link_df = fa_combo_link_df[(fa_combo_link_df['LINK'] == 'O-') | (fa_combo_link_df['LINK'] == 'P-')]
                if not op_link_df.empty:
                    op_link_df.is_copy = False
                    op_link_df.drop(['LINK'], axis = 1 , inplace=True)
                    if len(fa_df_header_lst) == 1:
                        op_link_df['DISCRETE_ABBR'] = (op_link_df['CLASS'] + '(' +
                                                       op_link_df[fa_df_header_lst[0]].str.strip('FA') + ')')
                    elif len(fa_df_header_lst) == 2:
                        op_link_df['DISCRETE_ABBR'] = (op_link_df['CLASS'] + '(' +
                                                       op_link_df[fa_df_header_lst[0]].str.strip('FA') + '_' +
                                                       op_link_df[fa_df_header_lst[1]].str.strip('FA') + ')')
                        if NameParserFA(lipid_class).lipid_fa_dct[lipid_class][4] == 1:
                            op_link_df['DISCRETE_ABBR'] = op_link_df['DISCRETE_ABBR'].str.replace(r'_', '')
                    elif len(fa_df_header_lst) == 3:
                        op_link_df['DISCRETE_ABBR'] = (op_link_df['CLASS'] + '(' +
                                                       op_link_df[fa_df_header_lst[0]].str.strip('FA') + '_' +
                                                       op_link_df[fa_df_header_lst[1]].str.strip('FA') + '_' +
                                                       op_link_df[fa_df_header_lst[2]].str.strip('FA') + ')')
                    elif len(fa_df_header_lst) == 4:
                        op_link_df['DISCRETE_ABBR'] = (op_link_df['CLASS'] + '(' +
                                                       op_link_df[fa_df_header_lst[0]].str.strip('FA') + '_' +
                                                       op_link_df[fa_df_header_lst[1]].str.strip('FA') + '_' +
                                                       op_link_df[fa_df_header_lst[2]].str.strip('FA') + '_' +
                                                       op_link_df[fa_df_header_lst[3]].str.strip('FA') + ')')
                    # TODO to the same for all the length( can also go as a function) ( georgia: 19.2.2019)
                    fa_combo_df = fa_link_df.append((op_link_df))
                else:
                    fa_combo_df = fa_link_df
            else:
                fa_combo_df = fa_link_df
            print('[INFO] --> Number of predicted lipids (exact position): ', fa_combo_df.shape[0])
        # Compine: in the above section (georgia: 19.2.2019)
        # if lipid_class in ['PA', 'PC', 'PE', 'PG', 'PI', 'PS', 'DG', 'SM']:
        #
        #     fa_combo_link_df = fa_combo_df
        #     fa_combo_link_df.is_copy = False
        #     fa_combo_link_df['LINK'] = fa_combo_link_df['FA1'].str[0:2]
        #     fa_link_df = fa_combo_link_df[fa_combo_link_df['LINK'] == 'FA']
        #
        #     fa_link_df.is_copy = False
        #     fa_link_df.drop(['LINK', 'CLASS'], axis=1, inplace=True)
        #     # fa_link_df.values.argsort(kind='mergesort')
        #     # fa_link_df.drop(columns=['CLASS'], inplace=True)
        #     fa_link_df.values.sort(kind='mergesort')  # safe sort by numpy
        #     fa_link_df['CLASS'] = lipid_class
        #     fa_link_df['DISCRETE_ABBR'] = (fa_link_df['CLASS'] + '(' +
        #                                    fa_link_df['FA1'].str.strip('FA') + '_' +
        #                                    fa_link_df['FA2'].str.strip('FA') + ')')
        #     fa_link_df.sort_values(by='DISCRETE_ABBR', inplace=True)
        #
        #     if lipid_class in ['PC', 'PE']:
        #         op_link_df = fa_combo_link_df[(fa_combo_link_df['LINK'] == 'O-') | (fa_combo_link_df['LINK'] == 'P-')]
        #         if not op_link_df.empty:
        #             op_link_df.is_copy = False
        #             op_link_df.drop(['LINK'], axis=1, inplace=True)
        #             op_link_df['DISCRETE_ABBR'] = (op_link_df['CLASS'] + '(' +
        #                                            op_link_df['FA1'].str.strip('FA') + '_' +
        #                                            op_link_df['FA2'].str.strip('FA') + ')')
        #             op_link_df.sort_values(by='DISCRETE_ABBR', inplace=True)
        #
        #             fa_combo_df = fa_link_df.append(op_link_df)
        #             del op_link_df
        #     else:
        #         fa_combo_df = fa_link_df
        #
        #     del fa_combo_link_df
        #     del fa_link_df
        #     print('[INFO] --> Number of predicted lipids (exact position): ', fa_combo_df.shape[0])
        #
        # elif lipid_class in ['LPA', 'LPC', 'LPE', 'LPG', 'LPI', 'LPS']:
        #
        #     fa_combo_link_df = fa_combo_df
        #     fa_combo_link_df.is_copy = False
        #
        #     fa_combo_link_df['LINK'] = fa_combo_link_df['FA1'].str[0:2]
        #     fa_link_df = fa_combo_link_df[fa_combo_link_df['LINK'] == 'FA']
        #
        #     fa_link_df.is_copy = False
        #     fa_link_df.drop(['LINK', 'CLASS'], axis=1, inplace=True)
        #     # fa_link_df.values.argsort(kind='mergesort')
        #     # fa_link_df.drop(columns=['CLASS'], inplace=True)
        #     # fa_link_df.values.sort(kind='mergesort')  # safe sort by numpy
        #     fa_link_df['CLASS'] = lipid_class
        #
        #     fa_link_df['DISCRETE_ABBR'] = (fa_link_df['CLASS'] + '(' +
        #                                    fa_link_df['FA1'].str.strip('FA') + ')')
        #     fa_link_df.sort_values(by='DISCRETE_ABBR', inplace=True)
        #
        #     if lipid_class in ['LPC', 'LPE']:
        #         op_link_df = fa_combo_link_df[(fa_combo_link_df['LINK'] == 'O-') | (fa_combo_link_df['LINK'] == 'P-')]
        #         if not op_link_df.empty:
        #             op_link_df.is_copy = False
        #             op_link_df.drop(['LINK'], axis=1, inplace=True)
        #             op_link_df['DISCRETE_ABBR'] = (op_link_df['CLASS'] + '(' +
        #                                            op_link_df['FA1'].str.strip('FA') + ')')
        #             op_link_df.sort_values(by='DISCRETE_ABBR', inplace=True)
        #
        #             fa_combo_df = fa_link_df.append(op_link_df)
        #             del op_link_df
        #     else:
        #         fa_combo_df = fa_link_df
        #
        #     del fa_combo_link_df
        #     del fa_link_df
        #     print('[INFO] --> Number of predicted lipids (exact position): ', fa_combo_df.shape[0])
        #
        # elif lipid_class in ['TG']:
        #     fa_combo_link_df = fa_combo_df
        #     fa_combo_link_df.is_copy = False
        #     fa_combo_link_df['LINK'] = fa_combo_link_df['FA1'].str[0:2]
        #     fa_link_df = fa_combo_link_df[fa_combo_link_df['LINK'] == 'FA']
        #
        #     fa_link_df.is_copy = False
        #     fa_link_df.drop(['LINK'], axis=1, inplace=True)
        #     fa_link_df.values.sort(kind='mergesort')  # safe sort by numpy
        #     fa_link_df['DISCRETE_ABBR'] = (fa_link_df['CLASS'] + '(' +
        #                                    fa_link_df['FA1'].str.strip('FA') + '_' +
        #                                    fa_link_df['FA2'].str.strip('FA') + '_' +
        #                                    fa_link_df['FA3'].str.strip('FA') + ')')
        #     fa_link_df.sort_values(by='DISCRETE_ABBR', inplace=True)
        #     op_link_df = fa_combo_link_df[(fa_combo_link_df['LINK'] == 'O-') | (fa_combo_link_df['LINK'] == 'P-')]
        #     if not op_link_df.empty:
        #         op_link_df.is_copy = False
        #         op_link_df.drop(['LINK'], axis=1, inplace=True)
        #         op_link_df['DISCRETE_ABBR'] = (op_link_df['CLASS'] + '(' +
        #                                        op_link_df['FA1'].str.strip('FA') + '_' +
        #                                        op_link_df['FA2'].str.strip('FA') + '_' +
        #                                        op_link_df['FA3'].str.strip('FA') + ')')
        #         op_link_df.sort_values(by='DISCRETE_ABBR', inplace=True)
        #         fa_combo_df = fa_link_df.append(op_link_df)
        #         del op_link_df
        #     else:
        #         fa_combo_df = fa_link_df
        #
        #     del fa_link_df
        #     del fa_combo_link_df
        #     print('[INFO] --> Number of predicted lipids (exact position): ', fa_combo_df.shape[0])
        #
        # elif lipid_class in ['CL']:
        #     fa_combo_df.values.sort(kind='mergesort')  # safe sort by numpy
        #     print('[INFO] --> Number of predicted lipids (exact position): ', fa_combo_df.shape[0])
        #     fa_combo_df['DISCRETE_ABBR'] = (fa_combo_df['CLASS'] + '(' +
        #                                     fa_combo_df['FA1'].str.strip('FA') + '_' +
        #                                     fa_combo_df['FA2'].str.strip('FA') + '_' +
        #                                     fa_combo_df['FA3'].str.strip('FA') + '_' +
        #                                     fa_combo_df['FA4'].str.strip('FA') + ')')
        #     fa_combo_df.sort_values(by='DISCRETE_ABBR', inplace=True)
        #     print('[INFO] --> Number of predicted lipids (exact position): ', fa_combo_df.shape[0])
        # elif lipid_class in ['Cer']:
        #     fa_link_df = fa_combo_df
        #
        #     fa_link_df.is_copy = False
        #     fa_link_df['DISCRETE_ABBR'] = (fa_link_df['CLASS'] + '(' +
        #                                    fa_link_df['Base'].str.strip('FA') + '_' +
        #                                    fa_link_df['FA1'].str.strip('FA') + ')')
        #     fa_link_df.sort_values(by='DISCRETE_ABBR', inplace=True)
        #
        #     fa_combo_df = fa_link_df
        #
        #     del fa_link_df
        #     print('[INFO] --> Number of predicted lipids (exact position): ', fa_combo_df.shape[0])
        # else:
        #     fa_combo_df['DISCRETE_ABBR'] = ''
        #     print('[WARNING] !!! Number of predicted lipids (exact position): 0')

        if position is False:
            print('[INFO] --> Use discrete form for identification ...')
            fa_combo_lite_df = fa_combo_df.drop_duplicates(subset=['DISCRETE_ABBR'], keep='first')
            print('[INFO] --> Number of predicted lipids (discrete form): ', fa_combo_lite_df.shape[0])
        else:
            fa_combo_lite_df = fa_combo_df

        fa_combo_lite_df.is_copy = False
        fa_combo_lite_df['idx'] = fa_combo_lite_df['DISCRETE_ABBR']
        fa_combo_lite_df.set_index('idx', drop=True, inplace=True)

        lipid_comb_dct = fa_combo_lite_df.to_dict(orient='index')

        return lipid_comb_dct


    def calc_fragments_geo(self, lipid_dct, charge='', ms2_ppm=100):

        # m_formula = lipid_dct['FORMULA']
        fa_header_list= NameParserFA(lipid_dct['CLASS']).lipid_fa_dct[lipid_dct['CLASS']][1]
        # was usuful when they were the Base fragment in a separate entry in the list
        # if NameParserFA(lipid_dct['CLASS']).lipid_fa_dct[lipid_dct['CLASS']][2] is not None:
        #     fa_header_list = [NameParserFA(lipid_dct['CLASS']).lipid_fa_dct[lipid_dct['CLASS']][2]] + fa_header_list
        m_exactmass = lipid_dct['EXACTMASS']
        m_class = lipid_dct['CLASS']

        # Note: need to check if this section is neccessary otherwise should be removed
        # Note: this section need to improve to give the correct water losses for the different ceramides base
        # Future
        if NameParserFA(lipid_dct['CLASS']).lipid_mode_dct[m_class][charge][3] is not None:
            print (NameParserFA(lipid_dct['CLASS']).lipid_mode_dct[m_class][charge][3])
            for frag in NameParserFA(lipid_dct['CLASS']).lipid_mode_dct[m_class][charge][3]:
                lipid_dct['{f}_ABBR'.format(f=frag)] = frag.replace('X', NameParserFA(lipid_dct['CLASS']).lipid_mode_dct[m_class][charge][4])
                lipid_dct['{f}_MZ'.format(f=frag)] = round(
                    m_exactmass + NameParserFA(lipid_dct['CLASS']).loss_dct[frag], 6)
                low_v = round(
                        ppm_window_para(lipid_dct['{f}_MZ'.format(f=frag)], ms2_ppm * -1), 6)
                high_v = round(ppm_window_para(lipid_dct['{f}_MZ'.format(f=frag)], ms2_ppm), 6)
                lipid_dct['{f}_Q'.format(f=frag)] = (low_v.astype(str) + ' <= mz <= '
                                                                            + high_v.astype(str))
                # Comment: below section was for an alternative reason but at the end was not necessary thats it why the above section was added later
                # for k_h in fa_header_list:
                #     lipid_dct['{f}_ABBR'.format(f= frag.replace('FA', k_h))] = frag.replace('FA', lipid_dct[k_h])
                #     lipid_dct['{f}_MZ'.format(f=frag.replace('FA', k_h))] = round(
                #         m_exactmass - lipid_dct['{k}_EXACTMASS'.format(k=k_h)] + NameParserFA().loss_dct[frag], 6)
                #     low_v = round(
                #         ppm_window_para(lipid_dct['{f}_MZ'.format(f=frag.replace('FA', k_h))], ms2_ppm * -1), 6)
                #     high_v = round(ppm_window_para(lipid_dct['{f}_MZ'.format(f=frag.replace('FA', k_h))], ms2_ppm), 6)
                #     lipid_dct['{f}_Q'.format(f=frag.replace('FA', k_h))] = (low_v.astype(str) + ' <= mz <= '
                #                                                             + high_v.astype(str))
        # # else:
        #     for frag in NameParserFA().lipid_mode_dct[m_class][charge][3]:
        #         for k_h in fa_header_list:
        #             lipid_dct['{f}_ABBR'.format(f= frag.replace('FA', k_h))] = frag.replace('FA', lipid_dct[k_h])
        #             lipid_dct['{f}_MZ'.format(f=frag.replace('FA', k_h))] = round(
        #                 m_exactmass - lipid_dct['{k}_EXACTMASS'.format(k=k_h)] + NameParserFA().loss_dct[frag], 6)
        #             low_v = round(
        #                 ppm_window_para(lipid_dct['{f}_MZ'.format(f=frag.replace('FA', k_h))], ms2_ppm * -1), 6)
        #             high_v = round(ppm_window_para(lipid_dct['{f}_MZ'.format(f=frag.replace('FA', k_h))], ms2_ppm), 6)
        #             lipid_dct['{f}_Q'.format(f=frag.replace('FA', k_h))] = (low_v.astype(str) + ' <= mz <= '
        #                                                                     + high_v.astype(str))
        return lipid_dct

    # Delet : will be delete was replace by the above (georgia: 11.10.2019)
    # @staticmethod
    # def calc_fragments(lipid_dct, charge='', ms2_ppm=100):
    #
    #     # m_formula = lipid_dct['FORMULA']
    #     m_exactmass = lipid_dct['EXACTMASS']
    #     m_class = lipid_dct['CLASS']
    #
    #     h_exactmass = 1.0078250321
    #     na_exactmass = 22.98976967
    #     nh3_exactmass = 3 * 1.0078250321 + 14.0030740052
    #     ch3_exactmass = 12.0 + 3 * 1.0078250321
    #     nl_water = 2 * 1.0078250321 + 15.9949146221
    #     gly_mg_base_exactmass = 3 * 12.0 + 5 * 1.0078250321 + 15.9949146221
    #     fa1_abbr = lipid_dct['FA1'].strip('FA')
    #     fa2_abbr = lipid_dct['FA2'].strip('FA')
    #
    #     fa1_exactmass = lipid_dct['FA1_EXACTMASS']
    #     # Note: The reason of the below statement is because of the lyso species they have an FA2 column but no FA2_EXACTMASS (georgia: 14.2.2019)
    #     if 'FA2_EXACTMASS' in list(lipid_dct.keys()):
    #         fa2_exactmass = lipid_dct['FA2_EXACTMASS']
    #
    #     if m_class in ['PA', 'PE', 'PG', 'PI', 'PS', 'PIP', 'PL']:
    #
    #         lyso_str = 'L' + m_class
    #
    #         # create the abbreviation name for the Lyso fragments eg. LPE(18:0)-H]-_ABBR
    #         # without the loss of water
    #         lipid_dct['[LPL(FA1)-H]-_ABBR'] = '[%s(%s)-H]-' % (lyso_str, fa1_abbr)
    #         lipid_dct['[LPL(FA2)-H]-_ABBR'] = '[%s(%s)-H]-' % (lyso_str, fa2_abbr)
    #         # with the loss of water
    #         lipid_dct['[LPL(FA1)-H2O-H]-_ABBR'] = '[%s(%s)-H2O-H]-' % (lyso_str, fa1_abbr)
    #         lipid_dct['[LPL(FA2)-H2O-H]-_ABBR'] = '[%s(%s)-H2O-H]-' % (lyso_str, fa2_abbr)
    #
    #         # calculation of the exact mass for the different lyso fragments
    #         lipid_dct['[LPL(FA1)-H]-_MZ'] = round(m_exactmass - (fa2_exactmass - nl_water) - h_exactmass, 6)
    #         lipid_dct['[LPL(FA2)-H]-_MZ'] = round(m_exactmass - (fa1_exactmass - nl_water) - h_exactmass, 6)
    #         lipid_dct['[LPL(FA1)-H2O-H]-_MZ'] = round(m_exactmass - fa2_exactmass - h_exactmass, 6)
    #         lipid_dct['[LPL(FA2)-H2O-H]-_MZ'] = round(m_exactmass - fa1_exactmass - h_exactmass, 6)
    #
    #     elif m_class in ['PC']:
    #
    #         lyso_str = 'L' + m_class
    #         # The abbr. here is not exactly correct due to the compatibility issues with ranks core calc functions
    #         lipid_dct['[LPL(FA1)-H]-_ABBR'] = '[%s(%s)-CH3]-' % (lyso_str, fa1_abbr)
    #         lipid_dct['[LPL(FA2)-H]-_ABBR'] = '[%s(%s)-CH3]-' % (lyso_str, fa2_abbr)
    #         lipid_dct['[LPL(FA1)-H2O-H]-_ABBR'] = '[%s(%s)-H2O-CH3]-' % (lyso_str, fa1_abbr)
    #         lipid_dct['[LPL(FA2)-H2O-H]-_ABBR'] = '[%s(%s)-H2O-CH3]-' % (lyso_str, fa2_abbr)
    #
    #         lipid_dct['[LPL(FA1)-H]-_MZ'] = round(m_exactmass - (fa2_exactmass - nl_water) - ch3_exactmass, 6)
    #         lipid_dct['[LPL(FA2)-H]-_MZ'] = round(m_exactmass - (fa1_exactmass - nl_water) - ch3_exactmass, 6)
    #         lipid_dct['[LPL(FA1)-H2O-H]-_MZ'] = round(m_exactmass - fa2_exactmass - ch3_exactmass, 6)
    #         lipid_dct['[LPL(FA2)-H2O-H]-_MZ'] = round(m_exactmass - fa1_exactmass - ch3_exactmass, 6)
    #
    #     elif m_class in ['LPA', 'LPE', 'LPG', 'LPI', 'LPS', 'LPIP', 'LPL']:
    #         pass
    #
    #     elif m_class in ['LPC']:
    #         pass
    #
    #     elif m_class in ['TG']:
    #         # Here maybe should get the DG fragments
    #         # TODO(georgia.angelidou@uni-leipzig.de): create the section for theuniue fragments when there is TG
    #         #   Missing the fragments for the sodium adduct
    #
    #         # The different frgments for triacylglycerol names when neutral loss of the FA
    #         # Take the correspond information of the 3 FA
    #         fa3_abbr = lipid_dct['FA3'].strip('FA')
    #         fa3_exactmass = lipid_dct['FA3_EXACTMASS']
    #         dg_str = 'M'
    #         if charge in ['[M+Na]+']:
    #             fa1_Na_exactmass = lipid_dct['FA1_[FA-H+Na]_MZ']
    #             fa2_Na_exactmass = lipid_dct['FA2_[FA-H+Na]_MZ']
    #             fa3_Na_exactmass = lipid_dct['FA3_[FA-H+Na]_MZ']
    #
    #             lipid_dct['[M-(FA1)+Na]+_ABBR'] = '[%s-FA%s+Na]+' % (dg_str, fa1_abbr)
    #             lipid_dct['[M-(FA2)+Na]+_ABBR'] = '[%s-FA%s+Na]+' % (dg_str, fa2_abbr)
    #             lipid_dct['[M-(FA3)+Na]+_ABBR'] = '[%s-FA%s+Na]+' % (dg_str, fa3_abbr)
    #
    #             lipid_dct['[M-(FA1-H+Na)+H]+_ABBR'] = '[%s-(FA%s-H+Na)+H]+' % (dg_str, fa1_abbr)
    #             lipid_dct['[M-(FA2-H+Na)+H]+_ABBR'] = '[%s-(FA%s-H+Na)+H]+' % (dg_str, fa2_abbr)
    #             lipid_dct['[M-(FA3-H+Na)+H]+_ABBR'] = '[%s-(FA%s-H+Na)+H]+' % (dg_str, fa3_abbr)
    #
    #             lipid_dct['[M-(FA1)+Na]+_MZ'] = round(m_exactmass - fa1_exactmass + na_exactmass, 6)
    #             lipid_dct['[M-(FA2)+Na]+_MZ'] = round(m_exactmass - fa2_exactmass + na_exactmass, 6)
    #             lipid_dct['[M-(FA3)+Na]+_MZ'] = round(m_exactmass - fa3_exactmass + na_exactmass, 6)
    #
    #             lipid_dct['[M-(FA1-H+Na)+H]+_MZ'] = round(m_exactmass - fa1_Na_exactmass + na_exactmass, 6)
    #             lipid_dct['[M-(FA2-H+Na)+H]+_MZ'] = round(m_exactmass - fa2_Na_exactmass + na_exactmass, 6)
    #             lipid_dct['[M-(FA3-H+Na)+H]+_MZ'] = round(m_exactmass - fa3_Na_exactmass + na_exactmass, 6)
    #
    #             lipid_dct['[M-(FA1)+Na]+_MZ_LOW'] = ppm_window_para((m_exactmass - (fa1_exactmass) + na_exactmass),
    #                                                                 ms2_ppm * -1)
    #             lipid_dct['[M-(FA1)+Na]+_MZ_HIGH'] = ppm_window_para((m_exactmass - (fa1_exactmass) + na_exactmass),
    #                                                                  ms2_ppm)
    #             lipid_dct['[M-(FA1)+Na]+_Q'] = (
    #                     lipid_dct['[M-(FA1)+Na]+_MZ_LOW'].astype(str) + ' <= mz <= ' + lipid_dct[
    #                 '[M-(FA1)+Na]+_MZ_HIGH'].astype(str))
    #
    #             lipid_dct['[M-(FA2)+Na]+_MZ_LOW'] = ppm_window_para((m_exactmass - (fa2_exactmass) + na_exactmass),
    #                                                                 ms2_ppm * -1)
    #             lipid_dct['[M-(FA2)+Na]+_MZ_HIGH'] = ppm_window_para((m_exactmass - (fa2_exactmass) + na_exactmass),
    #                                                                  ms2_ppm)
    #             lipid_dct['[M-(FA2)+Na]+_Q'] = (
    #                     lipid_dct['[M-(FA2)+Na]+_MZ_LOW'].astype(str) + ' <= mz <= ' + lipid_dct[
    #                 '[M-(FA2)+Na]+_MZ_HIGH'].astype(str))
    #
    #             lipid_dct['[M-(FA3)+Na]+_MZ_LOW'] = ppm_window_para((m_exactmass - (fa3_exactmass) + na_exactmass),
    #                                                                 ms2_ppm * -1)
    #             lipid_dct['[M-(FA3)+Na]+_MZ_HIGH'] = ppm_window_para((m_exactmass - (fa3_exactmass) + na_exactmass),
    #                                                                  ms2_ppm)
    #             lipid_dct['[M-(FA3)+Na]+_Q'] = (
    #                     lipid_dct['[M-(FA3)+Na]+_MZ_LOW'].astype(str) + ' <= mz <= ' + lipid_dct[
    #                 '[M-(FA3)+Na]+_MZ_HIGH'].astype(str))
    #
    #             lipid_dct['[M-(FA1-H+Na)+H]+_MZ_LOW'] = ppm_window_para(
    #                 (m_exactmass - (fa1_Na_exactmass) + na_exactmass), ms2_ppm * -1)
    #             lipid_dct['[M-(FA1-H+Na)+H]+_MZ_HIGH'] = ppm_window_para(
    #                 (m_exactmass - (fa1_Na_exactmass) + na_exactmass), ms2_ppm)
    #             lipid_dct['[M-(FA1-H+Na)+H]+_Q'] = (
    #                     lipid_dct['[M-(FA1-H+Na)+H]+_MZ_LOW'].astype(str) + ' <= mz <= ' + lipid_dct[
    #                 '[M-(FA1-H+Na)+H]+_MZ_HIGH'].astype(str))
    #
    #             lipid_dct['[M-(FA2-H+Na)+H]+_MZ_LOW'] = ppm_window_para(
    #                 (m_exactmass - (fa2_Na_exactmass) + na_exactmass), ms2_ppm * -1)
    #             lipid_dct['[M-(FA2-H+Na)+H]+_MZ_HIGH'] = ppm_window_para(
    #                 (m_exactmass - (fa2_Na_exactmass) + na_exactmass), ms2_ppm)
    #             lipid_dct['[M-(FA2-H+Na)+H]+_Q'] = (
    #                     lipid_dct['[M-(FA2-H+Na)+H]+_MZ_LOW'].astype(str) + ' <= mz <= ' + lipid_dct[
    #                 '[M-(FA2-H+Na)+H]+_MZ_HIGH'].astype(str))
    #
    #             lipid_dct['[M-(FA3-H+Na)+H]+_MZ_LOW'] = ppm_window_para(
    #                 (m_exactmass - (fa3_Na_exactmass) + na_exactmass), ms2_ppm * -1)
    #             lipid_dct['[M-(FA3-H+Na)+H]+_MZ_HIGH'] = ppm_window_para(
    #                 (m_exactmass - (fa3_Na_exactmass) + na_exactmass), ms2_ppm)
    #             lipid_dct['[M-(FA3-H+Na)+H]+_Q'] = (
    #                     lipid_dct['[M-(FA3-H+Na)+H]+_MZ_LOW'].astype(str) + ' <= mz <= ' + lipid_dct[
    #                 '[M-(FA3-H+Na)+H]+_MZ_HIGH'].astype(str))
    #         else:
    #             # Neutral loss of a FA with a water
    #             lipid_dct['[M-(FA1)+H]+_ABBR'] = '[%s-FA%s+H]+' % (dg_str, fa1_abbr)
    #             lipid_dct['[M-(FA2)+H]+_ABBR'] = '[%s-FA%s+H]+' % (dg_str, fa2_abbr)
    #             lipid_dct['[M-(FA3)+H]+_ABBR'] = '[%s-FA%s+H]+' % (dg_str, fa3_abbr)
    #             # Neutral loss of a FA minus a water
    #             lipid_dct['[M-(FA1-H2O)+H]+_ABBR'] = '[%s-(FA%s-H2O)+H]+' % (dg_str, fa1_abbr)
    #             lipid_dct['[M-(FA2-H2O)+H]+_ABBR'] = '[%s-(FA%s-H2O)+H]+' % (dg_str, fa2_abbr)
    #             lipid_dct['[M-(FA3-H2O)+H]+_ABBR'] = '[%s-(FA%s-H2O)+H]+' % (dg_str, fa3_abbr)
    #
    #             lipid_dct['[M-(FA1)+H]+_MZ'] = round(m_exactmass - fa1_exactmass + h_exactmass, 6)
    #             lipid_dct['[M-(FA2)+H]+_MZ'] = round(m_exactmass - fa2_exactmass + h_exactmass, 6)
    #             lipid_dct['[M-(FA3)+H]+_MZ'] = round(m_exactmass - fa3_exactmass + h_exactmass, 6)
    #
    #             lipid_dct['[M-(FA1-H2O)+H]+_MZ'] = round(m_exactmass - (fa1_exactmass - nl_water) + h_exactmass, 6)
    #             lipid_dct['[M-(FA2-H2O)+H]+_MZ'] = round(m_exactmass - (fa2_exactmass - nl_water) + h_exactmass, 6)
    #             lipid_dct['[M-(FA3-H2O)+H]+_MZ'] = round(m_exactmass - (fa3_exactmass - nl_water) + h_exactmass, 6)
    #
    #             lipid_dct['[MG(FA1)-H2O+H]+_MZ_LOW'] = ppm_window_para((fa1_exactmass + gly_mg_base_exactmass),
    #                                                                    ms2_ppm * -1)
    #             lipid_dct['[MG(FA1)-H2O+H]+_MZ_HIGH'] = ppm_window_para((fa1_exactmass + gly_mg_base_exactmass),
    #                                                                     ms2_ppm)
    #             lipid_dct['[MG(FA1)-H2O+H]+_Q'] = (
    #                     lipid_dct['[MG(FA1)-H2O+H]+_MZ_LOW'].astype(str) + ' <= mz <= ' +
    #                     lipid_dct['[MG(FA1)-H2O+H]+_MZ_HIGH'].astype(str))
    #
    #             lipid_dct['[MG(FA2)-H2O+H]+_MZ_LOW'] = ppm_window_para((fa2_exactmass + gly_mg_base_exactmass),
    #                                                                    ms2_ppm * -1)
    #             lipid_dct['[MG(FA2)-H2O+H]+_MZ_HIGH'] = ppm_window_para((fa2_exactmass + gly_mg_base_exactmass),
    #                                                                     ms2_ppm)
    #             lipid_dct['[MG(FA2)-H2O+H]+_Q'] = (
    #                     lipid_dct['[MG(FA2)-H2O+H]+_MZ_LOW'].astype(str) + ' <= mz <= ' +
    #                     lipid_dct['[MG(FA2)-H2O+H]+_MZ_HIGH'].astype(str))
    #
    #             lipid_dct['[MG(FA3)-H2O+H]+_MZ_LOW'] = ppm_window_para((fa3_exactmass + gly_mg_base_exactmass),
    #                                                                    ms2_ppm * -1)
    #             lipid_dct['[MG(FA3)-H2O+H]+_MZ_HIGH'] = ppm_window_para((fa3_exactmass + gly_mg_base_exactmass),
    #                                                                     ms2_ppm)
    #             lipid_dct['[MG(FA3)-H2O+H]+_Q'] = (
    #                     lipid_dct['[MG(FA3)-H2O+H]+_MZ_LOW'].astype(str) + ' <= mz <= ' +
    #                     lipid_dct['[MG(FA3)-H2O+H]+_MZ_HIGH'].astype(str))
    #
    #             lipid_dct['[M-(FA1)+H]+_MZ_LOW'] = ppm_window_para((m_exactmass - fa1_exactmass + h_exactmass),
    #                                                                ms2_ppm * -1)
    #             lipid_dct['[M-(FA1)+H]+_MZ_HIGH'] = ppm_window_para((m_exactmass - fa1_exactmass + h_exactmass),
    #                                                                 ms2_ppm)
    #             lipid_dct['[M-(FA1)+H]+_Q'] = (lipid_dct['[M-(FA1)+H]+_MZ_LOW'].astype(str) + ' <= mz <= ' + lipid_dct[
    #                 '[M-(FA1)+H]+_MZ_HIGH'].astype(str))
    #
    #             lipid_dct['[M-(FA2)+H]+_MZ_LOW'] = ppm_window_para((m_exactmass - fa2_exactmass + h_exactmass),
    #                                                                ms2_ppm * -1)
    #             lipid_dct['[M-(FA2)+H]+_MZ_HIGH'] = ppm_window_para((m_exactmass - fa2_exactmass + h_exactmass),
    #                                                                 ms2_ppm)
    #             lipid_dct['[M-(FA2)+H]+_Q'] = (lipid_dct['[M-(FA2)+H]+_MZ_LOW'].astype(str) + ' <= mz <= ' + lipid_dct[
    #                 '[M-(FA2)+H]+_MZ_HIGH'].astype(str))
    #
    #             lipid_dct['[M-(FA3)+H]+_MZ_LOW'] = ppm_window_para((m_exactmass - fa3_exactmass + h_exactmass),
    #                                                                ms2_ppm * -1)
    #             lipid_dct['[M-(FA3)+H]+_MZ_HIGH'] = ppm_window_para((m_exactmass - fa3_exactmass + h_exactmass),
    #                                                                 ms2_ppm)
    #             lipid_dct['[M-(FA3)+H]+_Q'] = (lipid_dct['[M-(FA3)+H]+_MZ_LOW'].astype(str) + ' <= mz <= ' + lipid_dct[
    #                 '[M-(FA3)+H]+_MZ_HIGH'].astype(str))
    #
    #             lipid_dct['[M-(FA1-H2O)+H]+_MZ_LOW'] = ppm_window_para(
    #                 (m_exactmass - (fa1_exactmass - nl_water) + h_exactmass), ms2_ppm * -1)
    #             lipid_dct['[M-(FA1-H2O)+H]+_MZ_HIGH'] = ppm_window_para(
    #                 (m_exactmass - (fa1_exactmass - nl_water) + h_exactmass), ms2_ppm)
    #             lipid_dct['[M-(FA1-H2O)+H]+_Q'] = (
    #                     lipid_dct['[M-(FA1-H2O)+H]+_MZ_LOW'].astype(str) + ' <= mz <= ' + lipid_dct[
    #                 '[M-(FA1-H2O)+H]+_MZ_HIGH'].astype(str))
    #
    #             lipid_dct['[M-(FA2-H2O)+H]+_MZ_LOW'] = ppm_window_para(
    #                 (m_exactmass - (fa2_exactmass - nl_water) + h_exactmass), ms2_ppm * -1)
    #             lipid_dct['[M-(FA2-H2O)+H]+_MZ_HIGH'] = ppm_window_para(
    #                 (m_exactmass - (fa2_exactmass - nl_water) + h_exactmass), ms2_ppm)
    #             lipid_dct['[M-(FA2-H2O)+H]+_Q'] = (
    #                     lipid_dct['[M-(FA2-H2O)+H]+_MZ_LOW'].astype(str) + ' <= mz <= ' + lipid_dct[
    #                 '[M-(FA2-H2O)+H]+_MZ_HIGH'].astype(str))
    #
    #             lipid_dct['[M-(FA3-H2O)+H]+_MZ_LOW'] = ppm_window_para(
    #                 (m_exactmass - (fa3_exactmass - nl_water) + h_exactmass), ms2_ppm * -1)
    #             lipid_dct['[M-(FA3-H2O)+H]+_MZ_HIGH'] = ppm_window_para(
    #                 (m_exactmass - (fa3_exactmass - nl_water) + h_exactmass), ms2_ppm)
    #             lipid_dct['[M-(FA3-H2O)+H]+_Q'] = (
    #                     lipid_dct['[M-(FA3-H2O)+H]+_MZ_LOW'].astype(str) + ' <= mz <= ' + lipid_dct[
    #                 '[M-(FA3-H2O)+H]+_MZ_HIGH'].astype(str))
    #         # Fragments names when can occur 2 neutral losses of FA. 1 FA with the water and other without
    #         mg_str = 'MG'
    #         lipid_dct['[MG(FA1)-H2O+H]+_ABBR'] = '[%s(%s)-H2O+H]+' % (mg_str, fa1_abbr)
    #         lipid_dct['[MG(FA2)-H2O+H]+_ABBR'] = '[%s(%s)-H2O+H]+' % (mg_str, fa2_abbr)
    #         lipid_dct['[MG(FA3)-H2O+H]+_ABBR'] = '[%s(%s)-H2O+H]+' % (mg_str, fa3_abbr)
    #
    #         lipid_dct['[MG(FA1)-H2O+H]+_MZ'] = round(fa1_exactmass + gly_mg_base_exactmass, 6)
    #         lipid_dct['[MG(FA2)-H2O+H]+_MZ'] = round(fa2_exactmass + gly_mg_base_exactmass, 6)
    #         lipid_dct['[MG(FA3)-H2O+H]+_MZ'] = round(fa3_exactmass + gly_mg_base_exactmass, 6)
    #
    #         # TODO (georgia.angelidou@uni-leipzig.de): add the fragments of Na [sodium]
    #         # Fragments when there only 1 neutral loss from the TG.
    #
    #     elif m_class in ['DG']:
    #         mg_str = 'MG'
    #         lipid_dct['[MG(FA1)-H2O+H]+_ABBR'] = '[%s(%s)-H2O+H]+' % (mg_str, fa1_abbr)
    #         lipid_dct['[MG(FA2)-H2O+H]+_ABBR'] = '[%s(%s)-H2O+H]+' % (mg_str, fa2_abbr)
    #
    #         lipid_dct['[MG(FA1)-H2O+H]+_MZ'] = round(fa1_exactmass + gly_mg_base_exactmass, 6)
    #         lipid_dct['[MG(FA2)-H2O+H]+_MZ'] = round(fa2_exactmass + gly_mg_base_exactmass, 6)
    #
    #         lipid_dct['[MG(FA1)-H2O+H]+_MZ_LOW'] = ppm_window_para((fa1_exactmass + gly_mg_base_exactmass),
    #                                                                ms2_ppm * -1)
    #         lipid_dct['[MG(FA1)-H2O+H]+_MZ_HIGH'] = ppm_window_para((fa1_exactmass + gly_mg_base_exactmass), ms2_ppm)
    #         lipid_dct['[MG(FA1)-H2O+H]+_Q'] = (
    #                 lipid_dct['[MG(FA1)-H2O+H]+_MZ_LOW'].astype(str) + ' <= mz <= ' +
    #                 lipid_dct['[MG(FA1)-H2O+H]+_MZ_HIGH'].astype(str))
    #
    #         lipid_dct['[MG(FA2)-H2O+H]+_MZ_LOW'] = ppm_window_para((fa2_exactmass + gly_mg_base_exactmass),
    #                                                                ms2_ppm * -1)
    #         lipid_dct['[MG(FA2)-H2O+H]+_MZ_HIGH'] = ppm_window_para((fa2_exactmass + gly_mg_base_exactmass), ms2_ppm)
    #         lipid_dct['[MG(FA2)-H2O+H]+_Q'] = (
    #                 lipid_dct['[MG(FA2)-H2O+H]+_MZ_LOW'].astype(str) + ' <= mz <= ' +
    #                 lipid_dct['[MG(FA2)-H2O+H]+_MZ_HIGH'].astype(str))
    #
    #     else:
    #         # TODO (georgia.angelidou@uni-leipzig.de: Info for sphingomyelins
    #         pass
    #
    #     return lipid_dct

    # Note: Get also the usr_fa_df (georgia: 20.2.2019)
    def compose_lipid(self, param_dct, usr_fa_info_df, ms2_ppm=100):

        lipid_class = param_dct['lipid_class']
        lipid_charge = param_dct['charge_mode']

        if param_dct['exact_position'] == 'TRUE':
            position_set = True
        else:
            position_set = False

        usr_fa_df = pd.read_excel(param_dct['fa_whitelist'])
        usr_fa_df = usr_fa_df.fillna(value='F')

        tmp_columns = usr_fa_df.columns.tolist()

        usr_fa_df.columns = usr_fa_df.columns.str.upper()
        # COMPINE (georgia):  the below section was rearrange to one 9.01.19

        if lipid_class in self.all_lipid_class_list:
            if lipid_class in tmp_columns:
                pass
            elif 'PL' in tmp_columns or 'LPL' in tmp_columns:
                pass
            else:
                return False
        else:
            return False
        # if lipid_class in ['PL', 'PA', 'PC', 'PE', 'PG', 'PI', 'PS', 'SM']:
        #     if lipid_class in tmp_columns:
        #         pass
        #     elif 'PL' in tmp_columns:
        #         pass
        #     else:
        #         return False
        # elif lipid_class in ['LPL', 'LPA', 'LPC', 'LPE', 'LPG', 'LPI', 'LPS']:
        #     if lipid_class in tmp_columns:
        #         pass
        #     elif 'LPL' in tmp_columns or 'PL' in tmp_columns:
        #         pass
        #     else:
        #         return False
        #
        # elif lipid_class in ['TG', 'DG']:
        #     if lipid_class in tmp_columns:
        #         pass
        #     else:
        #         return False
        # else:
        #     return False
        print('[INFO] --> FA white list loaded ...')
        lipid_comb_dct = self.gen_all_comb(lipid_class, usr_fa_df, position_set)

        lipid_info_dct = {}

        abbr_parser = NameParserFA()
        elem_calc = ElemCalc()

        fa_header_lst = NameParserFA(lipid_class).lipid_fa_dct[lipid_class][1]
        # Comment: can be deleted
        # if NameParserFA().lipid_fa_dct[lipid_class][2] is not None:
        #     fa_header_lst = [NameParserFA().lipid_fa_dct[lipid_class][2]] + fa_header_lst

        for _lipid in list(lipid_comb_dct.keys()):
            _lipid_dct = lipid_comb_dct[_lipid]


            # _fa1_abbr = _lipid_dct['FA1']
            # _fa2_abbr = _lipid_dct['FA2']
            # _fa1_info_dct = abbr_parser.get_fa_info(_fa1_abbr)
            # _fa2_info_dct = abbr_parser.get_fa_info(_fa2_abbr)
            # for _fa1_k in list(_fa1_info_dct.keys()):
            #     _lipid_dct['FA1_' + _fa1_k] = _fa1_info_dct[_fa1_k]
            #
            # for _fa2_k in list(_fa1_info_dct.keys()):
            #     _lipid_dct['FA2_' + _fa2_k] = _fa2_info_dct[_fa2_k]

            # Question: is this actually usefull or not
            # Note: with the new way this can be avoided (georgia: 20.2.2019)
            # Since we define this at the begginin there is not possibilite to have to FA1 anf FA2
            # So it can change to the old and just leave the check if it is empty or not
            # _fa1_abbr = _lipid_dct['FA1']
            # if _fa1_abbr:
            #     _fa1_info_dct = abbr_parser.get_fa_info(_fa1_abbr)
            #     # Note: check if we really need all of this columns and keep only the most necessary ones (georgia: 13.2.2019)
            #     for _fa1_k in list(_fa1_info_dct.keys()):
            #         _lipid_dct['FA1_' + _fa1_k] = _fa1_info_dct[_fa1_k]
            # else:
            #     if 'FA2' in list(_lipid_dct.keys()):
            #         if _lipid_dct['FA2']:
            #             _lipid_dct['FA1'], _lipid_dct['FA2'] = _lipid_dct['FA2'], _lipid_dct['FA1']
            #             _fa1_abbr = _lipid_dct['FA1']
            #             _fa1_info_dct = abbr_parser.get_fa_info(_fa1_abbr)
            #             for _fa1_k in list(_fa1_info_dct.keys()):
            #                 _lipid_dct['FA1_' + _fa1_k] = _fa1_info_dct[_fa1_k]
            #     else:
            #         _fa1_info_dct = {}
            #
            # if 'FA2' in list(_lipid_dct.keys()):
            #     _fa2_abbr = _lipid_dct['FA2']
            #     if _fa2_abbr:
            #         _fa2_info_dct = abbr_parser.get_fa_info(_fa2_abbr)
            #         for _fa2_k in list(_fa2_info_dct.keys()):
            #             _lipid_dct['FA2_' + _fa2_k] = _fa2_info_dct[_fa2_k]
            # else:
            #     _fa2_abbr = ''
            #     _fa2_info_dct = {}
            _lipid_dct['M_DB'] = 0
            _lipid_dct['M_C'] = 0
            for f_k in fa_header_lst:
                _fa_lipid = usr_fa_info_df.loc[_lipid_dct[f_k]]
                for _fa_k in list(_fa_lipid.keys()):
                    # Note: Use a filter so it would not take values that are NAN (georgia: 21.2.2019)
                    if _fa_lipid[_fa_k] is not np.nan:
                        _lipid_dct[str(f_k) + '_' + str(_fa_k)] = _fa_lipid[_fa_k]
                _lipid_dct['M_DB'] = int(_lipid_dct['M_DB']) + int(_fa_lipid['DB'])
                _lipid_dct['M_C'] = int(_lipid_dct['M_C']) + int(_fa_lipid['C'])

            # Note: thing a way to a more unify way (georgia: 20.2.2019)
            print (usr_fa_info_df.loc[_lipid_dct[fa_header_lst[0]]])
            if usr_fa_info_df.loc[_lipid_dct[fa_header_lst[0]]]['LINK'] in ['FA', 'A']:
                lipid_bulk_str = '{pl}({c}:{db})'.format(pl=lipid_class,
                                                         c=_lipid_dct['M_C'],
                                                         db=_lipid_dct['M_DB'])
            elif usr_fa_info_df.loc[_lipid_dct[fa_header_lst[0]]]['LINK'] in ['SPB']:
                # Comment: This will not work in the case of alpha hydroxylated FA
                lipid_bulk_str = '{pl}({c}:{db};{o})'.format(pl=lipid_class,
                                                             c=_lipid_dct['M_C'],
                                                             db=_lipid_dct['M_DB'],
                                                             o= _lipid_dct['FA1_O'])
            else:
                lipid_bulk_str = '{pl}({lk}{c}:{db})'.format(pl=lipid_class,
                                                             lk= _lipid_dct[fa_header_lst[0]+'_'+'LINK'],
                                                         c=_lipid_dct['M_C'],
                                                         db=_lipid_dct['M_DB'])
            # TODO (georgia.angelidou@uni-leipzig.de): SM, Cer
            # if lipid_class in ['PA', 'PC', 'PE', 'PG', 'PI', 'PS', 'DG']:
            #     _lipid_dct['M_DB'] = _fa1_info_dct['DB'] + _fa2_info_dct['DB']
            #     # TODO(georgia.angelidou@uni-leipzig.de): not important (just keep in mind for future correction)
            #     # consideration the case if the user choose the fa2 position for the different link types
            #     # or in that they may mistype something
            #     if _fa1_info_dct['LINK'] in ['FA', 'A']:
            #         lipid_bulk_str = '{pl}({c}:{db})'.format(pl=lipid_class,
            #                                                  c=_fa1_info_dct['C'] + _fa2_info_dct['C'],
            #                                                  db=lipid_comb_dct[_lipid]['M_DB'])
            #     else:
            #         lipid_bulk_str = '{pl}({lk}{c}:{db})'.format(pl=lipid_class, lk=_fa1_info_dct['LINK'],
            #                                                      c=_fa1_info_dct['C'] + _fa2_info_dct['C'],
            #                                                      db=lipid_comb_dct[_lipid]['M_DB'])
            # elif lipid_class in ['LPA', 'LPC', 'LPE', 'LPG', 'LPI', 'LPS']:
            #     _lipid_dct['M_DB'] = _fa1_info_dct['DB']
            #     # TODO(georgia.angelidou@uni-leipzig.de): not important (just keep in mind for future correction)
            #     # consideration the case if the user choose the fa2 position for the different link types
            #     # or in that they may mistype something
            #     if _fa1_info_dct['LINK'] in ['FA', 'A']:
            #         lipid_bulk_str = '{pl}({c}:{db})'.format(pl=lipid_class,
            #                                                  c=_fa1_info_dct['C'],
            #                                                  db=lipid_comb_dct[_lipid]['M_DB'])
            #     else:
            #         lipid_bulk_str = '{pl}({lk}{c}:{db})'.format(pl=lipid_class, lk=_fa1_info_dct['LINK'],
            #                                                      c=_fa1_info_dct['C'],
            #                                                      db=lipid_comb_dct[_lipid]['M_DB'])
            # elif lipid_class in ['TG']:
            #     _fa3_abbr = _lipid_dct['FA3']
            #     _fa3_info_dct = abbr_parser.get_fa_info(_fa3_abbr)
            #
            #     for _fa3_k in _fa3_info_dct.keys():
            #         _lipid_dct['FA3_' + _fa3_k] = _fa3_info_dct[_fa3_k]
            #
            #     _lipid_dct['M_DB'] = _fa3_info_dct['DB'] + _fa2_info_dct['DB'] + _fa1_info_dct['DB']
            #     # Note: For TG in the current default not consider the different lipids with other type of bond
            #     # If stay like this need to be mention in somewhere for the user
            #     if _fa1_info_dct['LINK'] in ['FA', 'A']:
            #         lipid_bulk_str = '{tg}({c}:{db})'.format(tg=lipid_class,
            #                                                  c=(_fa1_info_dct['C'] + _fa2_info_dct['C']
            #                                                     + _fa3_info_dct['C']),
            #                                                  db=lipid_comb_dct[_lipid]['M_DB'])
            #     else:
            #         lipid_bulk_str = '{tg}({lk}{c}:{db})'.format(tg=lipid_class, lk=_fa1_info_dct['LINK'],
            #                                                      c=(_fa1_info_dct['C'] + _fa2_info_dct['C']
            #                                                         + _fa3_info_dct['C']),
            #                                                      db=lipid_comb_dct[_lipid]['M_DB'])
            # elif lipid_class in ['SM']:
            #     # TODO(georgia.angelidou@uni-leipzi.de): sphingomyelin support
            #     lipid_bulk_str = '{sm}({c}:{db})'.format(sm=lipid_class,
            #                                              c=_fa1_info_dct['C'] + _fa2_info_dct['C'],
            #                                              db=lipid_comb_dct[_lipid]['M_DB'])
            # elif lipid_class in ['Cer']:
            #     # Note: maybe in the future can be company with SM
            #     _base_abbr = _lipid_dct['Base']
            #     _base_info_dct = abbr_parser.get_fa_info_geo(_base_abbr, lipid_class, lipid_charge)
            #
            #     for _base_k in _base_info_dct.keys():
            #         _lipid_dct['Base_' + _base_k] = _base_info_dct[_base_k]
            #     # _lipid_dct['M_DB'] =
            #
            #     lipid_bulk_str = '{cer}({base}{c}:{db})'.format(cer=lipid_class, base=_base_info_dct['LINK'], c=(_fa1_info_dct['C'] + _base_info_dct['C']),
            #                                              db=int(_fa1_info_dct['DB']) + int(_base_info_dct['DB']))
            # else:
            #     lipid_bulk_str = ''

            _lipid_dct['BULK_ABBR'] = lipid_bulk_str

            _lipid_formula, _lipid_elem_dct = elem_calc.get_formula(lipid_bulk_str)

            _lipid_dct['FORMULA'] = _lipid_formula
            _lipid_dct['EXACTMASS'] = elem_calc.get_exactmass(_lipid_elem_dct)
            # Note: probably this is not needed for further so could be skip the df (georgia: 20.2.2019)
            for _elem_k in list(_lipid_elem_dct.keys()):
                _lipid_dct['M_' + _elem_k] = _lipid_elem_dct[_elem_k]

            # charged
            _chg_lipid_formula, _chg_lipid_elem_dct = elem_calc.get_formula(lipid_bulk_str, charge=lipid_charge)
            _lipid_dct[lipid_charge + '_FORMULA'] = _chg_lipid_formula
            _lipid_dct[lipid_charge + '_MZ'] = elem_calc.get_exactmass(_chg_lipid_elem_dct)

            # fragments
            # if lipid_class in ['Cer', 'TG']:
            _lipid_dct = self.calc_fragments_geo(_lipid_dct, charge=lipid_charge, ms2_ppm=ms2_ppm)
            # else:
            #     _lipid_dct = self.calc_fragments(_lipid_dct, charge=lipid_charge, ms2_ppm=ms2_ppm)

            # Question: for what reason is needed this table (georgia: 13.2.2019)
            lipid_info_dct[_lipid] = _lipid_dct
            del _lipid_dct

        # Question: how we create lipid_comb_dct (georgia: 13.2.2019)
        lipid_master_df = pd.DataFrame(lipid_comb_dct).T
        lipid_master_df.reset_index(drop=True, inplace=True)

        return lipid_master_df


if __name__ == '__main__':
    # TODO (georgia.angelidou@uni-leipzig.de): Upgrade to ceramide lipid composition
    fa_lst_file = r'../ConfigurationFiles/1-FA_Whitelist_cER.xlsx'
    # fa_lst_file = r'../ConfigurationFiles/1-FA_Whitelist_TG-DG.xlsx'

    # Note:
    # exact position means to consider the position from the FA white list that the user give but,
    # in the case that the user define 2 different FA for both positions then:
    # When it is false it will give only one option
    # and when it is TRUE to give both combinations that these 2 FA an make (in case of phospholipids)

    # usr_param_dct = {'fa_whitelist': fa_lst_file, 'lipid_class': 'Cer', 'charge_mode': '[M+H]+',
    #                  'exact_position': 'FALSE'}

    usr_param_dct = {'fa_whitelist': fa_lst_file, 'lipid_class': 'LPC', 'charge_mode': '[M+HCOO]-',
                     'exact_position': 'FALSE'}
    # usr_param_dct = {'fa_whitelist': fa_lst_file, 'lipid_class': 'TG', 'charge_mode': '[M+NH4]+',
    #                  'exact_position': 'FALSE'}

    composer = LipidComposer()
    calc_fa_df = composer.calc_fa_query(usr_param_dct['lipid_class'], usr_param_dct['charge_mode'],
                                        fa_lst_file, ms2_ppm=50)
    usr_lipid_master_df = composer.compose_lipid(usr_param_dct,  calc_fa_df,  ms2_ppm=30)
    print('[INFO] --> Lipid Master Table generated...')
    master_csv = r'../Temp/LipidMaster_Whitelist_%s.csv' % usr_param_dct['lipid_class']
    usr_lipid_master_df.to_csv(master_csv)
    # master_csv = r'../Temp/LipidMaster_Whitelist_TG_ML.csv'

    fa_csv = r'../Temp/LipidMaster_FAlist2_%s.csv' % usr_param_dct['lipid_class']

    # calc_fa_df = composer.calc_fa_query(usr_param_dct['lipid_class'], usr_param_dct['charge_mode'],
    #                                     fa_lst_file, ms2_ppm=50)

    if calc_fa_df is False:
        print('[ERROR] !!! Failed to generate FA info table ...\n')

    print(calc_fa_df.head())

    calc_fa_df.to_csv(fa_csv)
    print('[INFO] --> Finished...')
# -*- coding: utf-8 -*-
# Copyright 2015-2016 Zhixu Ni, AG Bioanalytik, BBZ, University of Leipzig.
# The software is currently  under development and is not ready to be released.
# A suitable license will be chosen before the official release of oxLPPdb.
# For more info please contact: zhixu.ni@uni-leipzig.de

import os

from matplotlib import pyplot as plt
import matplotlib as mpl
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib._png import read_png
import pandas as pd

from StructureScore import AssignStructure


def plot_spectra(mz_se, xic_dct, ms1_rt, ms2_rt, ms1_df, ms2_df,
                 fa_indicator, lyso_indicator, fa_list_csv, save_img_as=None):

    pr_mz = mz_se['mz']
    ms1_obs = mz_se['MS1_obs_mz']
    _usr_rt = mz_se['rt']
    _usr_abbr_bulk = mz_se['Abbreviation']
    _usr_pl_class = mz_se['Class']
    _usr_formula = mz_se['Formula']
    _usr_ms2_function = mz_se['function']
    _usr_ms2_scan_id = mz_se['scan_id']

    _fa_checker = 0
    _hg_checker = 0

    print ('Start looking for m/z', pr_mz)

    abbr_id = mz_se['Abbreviation']
    _mzlib_id = mz_se['Lib_mz']
    _func_id = mz_se['function']
    _scan_id = mz_se['scan_id']

    _ms1_pr_df = ms1_df[ms1_df['mz'] == ms1_obs]
    # check if ms1_obs is present in MS survey scan with abs i >= 1000
    if _ms1_pr_df.shape[0] > 0:
        _mz_zoom_query_str = ' %.2f < mz < %.2f' % (pr_mz - 2.1, pr_mz + 2.1)
        _ms_zoom_df = ms1_df.query(_mz_zoom_query_str)
        _ms_zoom_df = _ms_zoom_df.sort_values(by='i', ascending=False)

        print('_ms1_pr_df shape', _ms1_pr_df.shape)
        print(_ms1_pr_df)
        _ms_isotope_df = _ms_zoom_df.head(1)

        if _ms_isotope_df.get_value(_ms_isotope_df.index[0], 'mz') == _ms1_pr_df.get_value(_ms1_pr_df.index[0], 'mz'):
            print('>>> Isotope checker=====> passed! >>>')

            xic_df = xic_dct[ms1_obs]

            _auto_ident_chker = 0

            # Generate A4 image in landscape
            fig, pic_array = plt.subplots(nrows=3, ncols=2, figsize=(11.692, 8.267), sharex=False,
                                          sharey=False)
            # Make better spacing between subplots
            plt.tight_layout()
            xic_pic = pic_array[0, 0]
            msms_pic = pic_array[0, 1]
            ms_pic = pic_array[1, 0]
            msms_low_pic = pic_array[1, 1]
            ms_zoom_pic = pic_array[2, 0]
            msms_high_pic = pic_array[2, 1]

            xic_pic.tick_params(axis='both', which='major', labelsize=10)
            msms_pic.tick_params(axis='both', which='major', labelsize=10)
            ms_pic.tick_params(axis='both', which='major', labelsize=10)
            msms_low_pic.tick_params(axis='both', which='major', labelsize=10)
            ms_zoom_pic.tick_params(axis='both', which='major', labelsize=10)
            msms_high_pic.tick_params(axis='both', which='major', labelsize=10)

            # ms spectrum start
            ms_pic.stem(ms1_df['mz'].tolist(), ms1_df['i'].tolist(),
                        'blue', lw=4, markerfmt=" ")
            _dash_i = [ms1_df['i'].max()]
            print(_dash_i)
            print(_ms1_pr_df['mz'])
            ms_pic.stem(_ms1_pr_df['mz'], _dash_i, ':', 'yellow', markerfmt=" ")
            ms_pic.stem(_ms1_pr_df['mz'], _ms1_pr_df['i'], 'red', lw=4, markerfmt=" ")

            ms_pic.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
            ms_pic.set_xlabel("m/z", fontsize=10, labelpad=-1)
            ms_pic.set_ylabel("Intensity", fontsize=10)
            ms_pic.set_ylim([0, max(ms1_df['i'].tolist()) * 1.3])

            # add annotation
            _ms_pkl_top_df = ms1_df.sort_values(by='i', ascending=False).head(10)
            _ms_pkl_top_peak_list = zip(_ms_pkl_top_df['mz'].tolist(), _ms_pkl_top_df['i'].tolist())
            for _ms_pkl_top_peak in _ms_pkl_top_peak_list:
                _ms_pkl_top_peak_str = '%.4f' % _ms_pkl_top_peak[0]
                _ms_pkl_top_peak_y = ((max(_ms_pkl_top_df['i'].tolist()) * 1.3) * 0.175 +
                                      _ms_pkl_top_peak[1])
                ms_pic.text(_ms_pkl_top_peak[0], _ms_pkl_top_peak_y, _ms_pkl_top_peak_str,
                            rotation=90, fontsize=6)

            ms_zoom_pic.stem(_ms_zoom_df['mz'].tolist(), _ms_zoom_df['i'].tolist(),
                             'black', lw=4, markerfmt=" ")

            ms_zoom_pic.stem(_ms1_pr_df['mz'], _ms1_pr_df['i'], 'red', lw=4, markerfmt=" ")

            ms_zoom_pic.set_xlim([pr_mz - 2.1, pr_mz + 2.1])
            ms_zoom_pic.set_ylim([0, max(_ms_zoom_df['i'].tolist()) * 1.3])
            ms_zoom_pic.ticklabel_format(style='sci', axis='y', scilimits=(0, 0), fontsize=10)
            ms_zoom_pic.ticklabel_format(axis='x', useOffset=False, fontsize=10)
            ms_zoom_pic.set_xlabel("m/z", fontsize=10, labelpad=-1)
            ms_zoom_pic.set_ylabel("Intensity", fontsize=10)

            # add annotation
            # _ms_zoom_peak_list = zip(_ms_zoom_df['mz'].tolist(), _ms_zoom_df['i'].tolist())
            # print('_ms_zoom_df')
            # print(_ms_zoom_df)

            _ms_zoom_top_df = _ms_zoom_df.sort_values(by='i', ascending=False).head(10)
            _ms_zoom_peak_list = zip(_ms_zoom_top_df['mz'].tolist(),
                                     _ms_zoom_top_df['i'].tolist())

            for _ms_zoom_peak in _ms_zoom_peak_list:
                _ms_zoom_peak_str = '%.4f' % _ms_zoom_peak[0]
                _ms_zoom_peak_y = (max(_ms_zoom_df['i'].tolist()) * 1.3) * 0.005 + _ms_zoom_peak[1]
                ms_zoom_pic.text(_ms_zoom_peak[0], _ms_zoom_peak_y, _ms_zoom_peak_str,
                                 fontsize=6)

            # XIC spectrum start
            xic_rt_lst = xic_df['rt'].tolist()
            xic_i_lst = xic_df['i'].tolist()
            xic_pic.plot(xic_rt_lst, xic_i_lst, alpha=0.3)
            xic_pic.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
            xic_pic.stem([ms1_rt], [max(xic_i_lst)], ':', markerfmt=" ")
            xic_pic.stem([ms2_rt], [max(xic_i_lst)], ':', markerfmt=" ")
            xic_pic.text(ms1_rt - 0.3, max(xic_i_lst) * 0.98, 'MS', fontsize=10)
            xic_pic.text(ms2_rt, max(xic_i_lst) * 0.98, 'MS/MS', fontsize=10)
            xic_pic.set_xlabel("RT (min)", fontsize=10, labelpad=-1)
            xic_pic.set_ylabel("Intensity", fontsize=10)

            # msms spectrum start
            msms_pic.stem(ms2_df['mz'].tolist(), ms2_df['i'].tolist(), 'blue', lw=2,
                          markerfmt=" ")
            msms_pic.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
            msms_pic.set_xlabel("m/z", fontsize=10, labelpad=-1)
            msms_pic.set_ylabel("Intensity", fontsize=10)
            msms_pic.set_xlim([min(ms2_df['mz'].tolist()) - 1, pr_mz + 20])
            msms_pic.set_ylim([0, max(ms2_df['i'].tolist()) * 1.3])

            # add annotations
            _topms2_df = ms2_df.sort_values(by='i', ascending=False)
            _topms2_df = _topms2_df.head(20)
            _msms_peak_list = zip(_topms2_df['mz'].tolist(), _topms2_df['i'].tolist())
            for _msms_peak in _msms_peak_list:
                _msms_peak_str = '%.4f' % _msms_peak[0]
                _msms_peak_y = (max(ms2_df['i'].tolist()) * 1.3) * 0.175 + _msms_peak[1]
                msms_pic.text(_msms_peak[0], _msms_peak_y, _msms_peak_str,
                              rotation=90, fontsize=6)
            # _pr_mol = Chem.MolFromSmiles(_pr_smi)
            # AllChem.Compute2DCoords(_pr_mol)
            #
            # # arr_hand = read_png('/save_img_as/to/this/image.png')
            # _pr_img = Draw.MolToImage(_pr_mol, size=(450, 300))
            # imagebox = OffsetImage(_pr_img)
            # xy = [max(ms2_df['mz'].tolist()) * 0.5, max(ms2_df['i'].tolist())]
            # _pr_ab = AnnotationBbox(imagebox, xy, xycoords='data', xybox=(90., -60.),
            #                         boxcoords="offset points", frameon=True)
            # msms_pic.add_artist(_pr_ab)

            # for _usr_mz in [_sn1_mz, _sn2_mz]:
            #     _msms_top_df = ms2_df.sort(columns='i', ascending=False)
            #     _msms_top_df = _msms_top_df.head(10)
            #     _query_str = '%f - %f <= mz <= %f + %f' % (_usr_mz, 0.25, _usr_mz, 0.25)
            #     _snms2_df = _msms_top_df.query(_query_str)
            #     _snms2_df = _snms2_df.sort(columns='i', ascending=False)
            #     # print _snms2_df.head(2)
            #     try:
            #         msms_pic.stem([_snms2_df['mz'].tolist()[0]], [_snms2_df['i'].tolist()[0]],
            #                       'red', lw=4, markerfmt=" ")
            #         _fa_checker += 1
            #     except:
            #         print('no sn fit')

            # msms spectrum zoomed below 355 start
            _msms_low_df = ms2_df.query('mz < 350')
            if len(_msms_low_df['mz'].tolist()) > 0:
                msms_low_pic.stem(_msms_low_df['mz'].tolist(),
                                  _msms_low_df['i'].tolist(),
                                  'black', lw=2, markerfmt=" ")
                msms_low_pic.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
                msms_low_pic.set_xlabel("m/z", fontsize=10, labelpad=-1)
                msms_low_pic.set_ylabel("Intensity", fontsize=10)
                msms_low_pic.set_xlim([min(_msms_low_df['mz'].tolist()) - 1, 350])
                msms_low_pic.set_ylim([0, max(_msms_low_df['i'].tolist()) * 1.3])
                # PC HG form DOI: 10.1021/acs.jproteome.5b00169
                # for _usr_mz in [168.0358, 224.0693, 242.0798]:
                #     _query_str = '%f - %f <= mz <= %f + %f' % (_usr_mz, 0.25, _usr_mz, 0.25)
                #     _snms2_df = ms2_df.query(_query_str)
                #     _snms2_df = _snms2_df.sort(columns='i', ascending=False)
                #     # print _snms2_df.head(2)
                #     try:
                #         msms_low_pic.stem([_snms2_df['mz'].tolist()[0]],
                #                           [_snms2_df['i'].tolist()[0]], 'red', lw=4, markerfmt=" ")
                #         _hg_checker += 1
                #     except:
                #         print('no sn fit')

                # add annotations
                _top_msms_low_df = _msms_low_df.sort_values(by='i', ascending=False)
                _top_msms_low_df = _top_msms_low_df.head(20)
                _msms_low_peak_list = zip(_top_msms_low_df['mz'].tolist(),
                                          _top_msms_low_df['i'].tolist())
                for _msms_low_peak in _msms_low_peak_list:
                    _msms_low_peak_str = '%.4f' % _msms_low_peak[0]
                    _msms_low_peak_y = (max(_msms_low_df['i'].tolist()) * 1.3) * 0.175 + \
                                       _msms_low_peak[1]
                    msms_low_pic.text(_msms_low_peak[0], _msms_low_peak_y, _msms_low_peak_str,
                                      rotation=90, fontsize=6)
            else:
                pass

            # get identification
            (fa_df, fa_info_dct) = fa_indicator.indicate(ms2_df)

            if fa_info_dct is not None:
                # print fa_info
                fa_count = len(fa_info_dct['mz'])
                fa_count_lst = range(fa_count)
                _fa_name_lst = fa_info_dct['name']
                _fa_mz_lst = fa_info_dct['mz']
                _fa_i_lst = fa_info_dct['i']
                _fa_ppm_lst = fa_info_dct['ppm']
                _fa_delta_lst = fa_info_dct['D']

                fa_info_df = pd.DataFrame(fa_info_dct, columns=['name', 'mz', 'i', 'ppm'])
                fa_info_df = fa_info_df.sort_values(by='i', ascending=False)
                fa_info_df = fa_info_df.round({'mz': 4})
                # fa_info_df.index = range(1, len(fa_info['mz']) + 1)
                table_info_df = fa_info_df

                # print table_info_df.head(5)
                old_idx_lst = table_info_df.index.tolist()
                table_info_df.index = range(1, len(old_idx_lst) + 1)

                col_labels = table_info_df.columns.tolist()
                # col_labels = mz_info_df.head().tolist()
                row_labels = table_info_df.index.tolist()
                table_vals = map(list, table_info_df.values)
                try:
                    # the rectangle is where I want to place the table
                    fa_table = msms_pic.table(cellText=table_vals, rowLabels=row_labels,
                                              colWidths=[.10] * len(col_labels),
                                              colLabels=col_labels, loc='upper center')
                    fa_table.set_fontsize(5)
                    _auto_ident_chker += 1
                except IndexError:
                    pass
                    # table_props = the_table.properties()
                    # table_cells = table_props['child_artists']
                    # for cell in table_cells:
                    #     cell.set_height(0.12)

            # msms spectrum zoomed above 350 start
            _msms_high_df = ms2_df.query('mz > 350')
            if len(_msms_high_df['mz'].tolist()) > 0:
                msms_high_pic.stem(_msms_high_df['mz'].tolist(),
                                   _msms_high_df['i'].tolist(),
                                   'black', lw=4, markerfmt=" ")
                msms_high_pic.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
                msms_high_pic.set_xlabel("m/z", fontsize=10, labelpad=-1)
                msms_high_pic.set_ylabel("Intensity", fontsize=10)
                msms_high_pic.set_xlim([350, pr_mz + 20])
                msms_high_pic.set_ylim([0, max(_msms_high_df['i'].tolist()) * 1.3])

                # add annotations
                _top_msms_high_df = _msms_high_df.sort_values(by='i', ascending=False)
                _top_msms_high_df = _top_msms_high_df.head(20)
                _msms_high_peak_list = zip(_top_msms_high_df['mz'].tolist(),
                                           _top_msms_high_df['i'].tolist())
                for _msms_high_peak in _msms_high_peak_list:
                    _msms_high_peak_str = '%.4f' % _msms_high_peak[0]
                    _msms_high_peak_y = ((max(_msms_high_df['i'].tolist()) * 1.3) * 0.175 +
                                         _msms_high_peak[1])
                    msms_high_pic.text(_msms_high_peak[0], _msms_high_peak_y, _msms_high_peak_str,
                                       rotation=90, fontsize=6)
            else:
                pass

            # get Lyso identification
            (lyso_df, lyso_info_dct) = lyso_indicator.indicate(ms2_df, pr_mz, PLtype=_usr_pl_class)

            if lyso_info_dct is not None:
                # print lyso_info
                lyso_count = len(lyso_info_dct['mz'])
                lyso_count_lst = range(lyso_count)
                _lyso_name_lst = lyso_info_dct['name']
                _lyso_mz_lst = lyso_info_dct['mz']
                _lyso_i_lst = lyso_info_dct['i']
                _lyso_ppm_lst = lyso_info_dct['ppm']
                _lyso_delta_lst = lyso_info_dct['D']

                lyso_info_df = pd.DataFrame(lyso_info_dct, columns=['name', 'mz', 'i', 'ppm'])
                lyso_info_df = lyso_info_df.sort_values(by='i', ascending=False)
                lyso_info_df = lyso_info_df.round({'mz': 4})

                # print table_info_df.head(5)
                old_idx_lst = lyso_info_df.index.tolist()
                lyso_info_df.index = range(1, len(old_idx_lst) + 1)

                col_labels = lyso_info_df.columns.tolist()
                # col_labels = mz_info_df.head().tolist()
                row_labels = lyso_info_df.index.tolist()
                table_vals = map(list, lyso_info_df.values)
                # plot lyso table
                try:
                    # the rectangle is where I want to place the table
                    lyso_table = msms_high_pic.table(cellText=table_vals, rowLabels=row_labels,
                                                     colWidths=[.22, .1, .1, .1],
                                                     colLabels=col_labels, loc='upper center')
                    lyso_table.set_fontsize(7)
                    _auto_ident_chker += 1
                except IndexError:
                    pass

                # get assignment
                ident_struct = AssignStructure()
                _match_fa_df = pd.DataFrame()
                usr_std_fa_df = pd.read_csv(fa_list_csv)
                usr_std_fa_df['C'].astype(int)
                usr_std_fa_df['DB'].astype(int)
                for _ident_idx, _ident_row in usr_std_fa_df.iterrows():
                    pre_ident_fa_df = usr_std_fa_df
                    pre_ident_fa_df['abs'] = 0
                    tmp_fa = pre_ident_fa_df.ix[_ident_idx]['FA']
                    if tmp_fa in fa_info_dct['fa']:
                        _tmp_fa_idx = fa_info_dct['fa'].index(tmp_fa)
                        _tmp_i = fa_info_dct['abs'][_tmp_fa_idx]
                        pre_ident_fa_df.set_value(_ident_idx, 'abs', _tmp_i)
                        _match_fa_df = _match_fa_df.append(pre_ident_fa_df.ix[_ident_idx])
                _match_lyso_df = pd.DataFrame()
                for _ident_idx, _ident_row in usr_std_fa_df.iterrows():
                    pre_lyso_fa_df = usr_std_fa_df
                    pre_lyso_fa_df['type'] = ''
                    pre_lyso_fa_df['abs'] = 0
                    tmp_lyso = pre_lyso_fa_df.ix[_ident_idx]['FA']
                    lyso_info_zip_lst = zip(lyso_info_dct['type'], lyso_info_dct['fa'])
                    if ('Lyso-H2O', tmp_lyso) in lyso_info_zip_lst:
                        # _tmp_lyso_idx = lyso_info_dct['fa'].index(tmp_lyso)
                        # _tmp_type = lyso_info_dct['type'][_tmp_lyso_idx]
                        _tmp_lyso_idx = lyso_info_zip_lst.index(('Lyso-H2O', tmp_lyso))
                        _tmp_i = lyso_info_dct['abs'][_tmp_lyso_idx]
                        pre_lyso_fa_df.set_value(_ident_idx, 'type', 'Lyso-H2O')
                        pre_lyso_fa_df.set_value(_ident_idx, 'abs', _tmp_i)
                        _match_lyso_df = _match_lyso_df.append(pre_lyso_fa_df.ix[_ident_idx])
                    if ('Lyso', tmp_lyso) in lyso_info_zip_lst:
                        _tmp_lyso_idx = lyso_info_zip_lst.index(('Lyso', tmp_lyso))
                        _tmp_i = lyso_info_dct['abs'][_tmp_lyso_idx]
                        pre_lyso_fa_df.set_value(_ident_idx, 'type', 'Lyso')
                        pre_lyso_fa_df.set_value(_ident_idx, 'abs', _tmp_i)
                        _match_lyso_df = _match_lyso_df.append(pre_lyso_fa_df.ix[_ident_idx])

                print ('_match_fa_df', _match_fa_df.shape, '_match_lyso_df', _match_lyso_df.shape)

                _ident_df = ident_struct.check(abbr_id, _match_fa_df,
                                               _match_lyso_df, usr_std_fa_df)
                print ('_ident_df')
                print (_ident_df)

                if _ident_df.shape[0] > 0:
                    # print fa_info

                    _ident_table_df = _ident_df.loc[:, ['Abbr', 'Score']]
                    _ident_table_df = _ident_table_df.sort_values(by=['Score', 'Abbr'],
                                                                  ascending=[False, True])
                    # print table_info_df.head(5)
                    old_idx_lst = _ident_table_df.index.tolist()
                    _ident_table_df.index = range(1, len(old_idx_lst) + 1)

                    col_labels = _ident_table_df.columns.tolist()
                    # col_labels = mz_info_df.head().tolist()
                    row_labels = _ident_table_df.index.tolist()
                    table_vals = map(list, _ident_table_df.values)

                    try:
                        # the rectangle is where I want to place the table
                        fa_table = ms_pic.table(cellText=table_vals, rowLabels=row_labels,
                                                colWidths=[.2] * len(col_labels),
                                                colLabels=col_labels, loc='upper left')
                        fa_table.set_fontsize(6)
                        _auto_ident_chker += 1
                    except:
                        pass

                # if _auto_ident_chker > 0:
                # set title
                xic_title_str = 'XIC of m/z %.4f Abbr.: %s @ %.4f' % (ms1_obs, abbr_id, _mzlib_id)
                ms_title_str = 'MS @ %.3f min [top 1000]' % _usr_rt
                ms_zoom_title_str = 'MS zoomed'
                msms_title_str = ('MS/MS of m/z %.4f @ fuc %d - %.3f min [top 500]' %
                                  (pr_mz, _func_id, _usr_rt))
                msms_low_str = 'MS/MS zoomed below 350'
                msms_high_str = 'MS/MS zoomed above 350'

                xic_pic.set_title(xic_title_str, color='b', fontsize=10, y=0.98)
                ms_pic.set_title(ms_title_str, color='b', fontsize=10, y=0.98)
                ms_zoom_pic.set_title(ms_zoom_title_str, color='b', fontsize=10, y=0.98)
                msms_pic.set_title(msms_title_str, color='b', fontsize=10, y=0.98)
                msms_low_pic.set_title(msms_low_str, color='b', fontsize=10, y=0.98)
                msms_high_pic.set_title(msms_high_str, color='b', fontsize=10, y=0.98)

                print ('>>> >>> >>> try to plot >>> >>> >>>')

                plt.savefig(save_img_as, dpi=300)
                print ('=====> Image saved as: %s' % save_img_as)
                plt.close()
                _fa_checker = 0
                _hg_checker = 0
            else:
                pass
        else:
            print ('Isotopes >>>>>> PASS !!!!!!')
            plt.close()
            print ('Not identified !!!!!! =>> >>>>>>')

    else:
        print ('Corresponding MS1 to low >>>>>> PASS !!!!!!')
        plt.close()
        print ('Not identified !!!!!! =>> >>>>>>')
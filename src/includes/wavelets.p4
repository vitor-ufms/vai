/* -*- P4_16 -*- */
/* P4 program for calculating wavelets trasnform using the Haar wavelet */
/* Arthur Selle Jacobs (asjacobs@inf.ufrgs.br) */
/* INF-UFRGS / Princeton University Computer Science Department */
/* Briggette Roman Huaytalla (borhuaytalla@inf.ufrgs.br) */
/* INF-UFRGS */

#include "squares.p4"

/* size of register of max input signal */
const bit<32> NUMBER_PACKETS = 2000;

/*************************************************************************
*********************** R E G I S T E R S  *****************************
*************************************************************************/

/* register array to store the first timestamp measured so we can offsset the rest */
register<bit<32>>(1) timestamp_offset;

register<bit<32>>(1) signal_index;
register<bit<32>>(1) count_signal;

register<bit<32>>(NUMBER_PACKETS) values_index;
register<bit<32>>(NUMBER_PACKETS) values_global_timestamp;
register<bit<32>>(NUMBER_PACKETS) values_offset;
register<bit<48>>(NUMBER_PACKETS) values_division;
// register<bit<32>>(NUMBER_PACKETS) values_level_one_index;
// register<bit<32>>(NUMBER_PACKETS) values_level_two_index;
// register<bit<32>>(NUMBER_PACKETS) values_level_three_index;
// register<bit<32>>(NUMBER_PACKETS) values_level_four_index;
// register<bit<32>>(NUMBER_PACKETS) values_level_five_index;
// register<bit<32>>(NUMBER_PACKETS) values_level_six_index;
// register<bit<32>>(NUMBER_PACKETS) values_level_seven_index;
// register<bit<32>>(NUMBER_PACKETS) values_level_eight_index;
// register<bit<32>>(NUMBER_PACKETS) values_level_nine_index;
// register<bit<32>>(NUMBER_PACKETS) values_level_ten_index;

register<bit<32>>(1) next_level_zero_index;
register<bit<32>>(1) next_level_one_index;
register<bit<32>>(1) next_level_two_index;
register<bit<32>>(1) next_level_three_index;
register<bit<32>>(1) next_level_four_index;
register<bit<32>>(1) next_level_five_index;
register<bit<32>>(1) next_level_six_index;
register<bit<32>>(1) next_level_seven_index;
// register<bit<32>>(1) next_level_eight_index;
// register<bit<32>>(1) next_level_nine_index;

/* Current indexes for each decomposition level */
register<bit<32>>(1) level_one_index;
register<bit<32>>(1) level_two_index;
register<bit<32>>(1) level_three_index;
register<bit<32>>(1) level_four_index;
register<bit<32>>(1) level_five_index;
register<bit<32>>(1) level_six_index;
register<bit<32>>(1) level_seven_index;
register<bit<32>>(1) level_eight_index;

/* registers for signal, hp and lp coefficients at each level */
register<int<32>>(SIGNAL_SIZE) signal;

register<int<32>>(SIGNAL_SIZE / 2) level_one_hp_coeffs;
register<int<32>>(SIGNAL_SIZE / 2) level_one_lp_coeffs;

register<int<32>>(SIGNAL_SIZE / 4) level_two_hp_coeffs;
register<int<32>>(SIGNAL_SIZE / 4) level_two_lp_coeffs;

register<int<32>>(SIGNAL_SIZE / 8) level_three_hp_coeffs;
register<int<32>>(SIGNAL_SIZE / 8) level_three_lp_coeffs;

register<int<32>>(SIGNAL_SIZE / 16) level_four_hp_coeffs;
register<int<32>>(SIGNAL_SIZE / 16) level_four_lp_coeffs;

register<int<32>>(SIGNAL_SIZE / 32) level_five_hp_coeffs;
register<int<32>>(SIGNAL_SIZE / 32) level_five_lp_coeffs;

register<int<32>>(SIGNAL_SIZE / 64) level_six_hp_coeffs;
register<int<32>>(SIGNAL_SIZE / 64) level_six_lp_coeffs;

register<int<32>>(SIGNAL_SIZE / 128) level_seven_hp_coeffs;
register<int<32>>(SIGNAL_SIZE / 128) level_seven_lp_coeffs;

register<int<32>>(SIGNAL_SIZE / 256) level_eight_hp_coeffs;
register<int<32>>(SIGNAL_SIZE / 256) level_eight_lp_coeffs;

/**************************************************************************
**************  W A V E L E T S   P R O C E S S I N G   *******************
**************************************************************************/
control Wavelets(inout standard_metadata_t standard_metadata) {  
  SumOfSquares() squared;

  action level_one() {
    // calculate element of first wavelet decomposition level
    bit<32> idx_zero = 0;
    next_level_zero_index.read(idx_zero, 0);
    // signal_index.read(idx_zero, 0);

    // bit<32> idx_one = (idx_zero >> 1) - 1; // finds correct index of level 1 based on level 0

    bit<32> idx_one = 0;
    level_one_index.read(idx_one, 0);

    // number of points read depend on size of filter
    int<32> point_one = 0;
    int<32> point_two = 0;
    signal.read(point_one, idx_zero - 1);
    signal.read(point_two, idx_zero - 2);

    // simplified convolution of Haar wavelet coefficients, see notes for explanation
    int<32> hp_coeff = (point_one - point_two);
    int<32> lp_coeff = (point_two + point_one);

    // Normalization (division by sqrt(2) aproximation)
    int<32> hp_coeff_norm = (
      (hp_coeff << 15) + (hp_coeff << 13) + (hp_coeff << 12) + (hp_coeff << 10) + (hp_coeff <<  8) + (hp_coeff <<  2) + 
      (hp_coeff >>  1) + (hp_coeff >>  2) + (hp_coeff >>  3) + (hp_coeff >>  4) + (hp_coeff >>  7) + (hp_coeff >>  8) + 
      (hp_coeff >> 11) + (hp_coeff >> 12) + (hp_coeff >> 13) + (hp_coeff >> 14) + (hp_coeff >> 15) + (hp_coeff >> 16) ) >> 16;
    
    int<32> lp_coeff_norm = (
      (lp_coeff << 15) + (lp_coeff << 13) + (lp_coeff << 12) + (lp_coeff << 10) + (lp_coeff <<  8) + (lp_coeff <<  2) + 
      (lp_coeff >>  1) + (lp_coeff >>  2) + (lp_coeff >>  3) + (lp_coeff >>  4) + (lp_coeff >>  7) + (lp_coeff >>  8) + 
      (lp_coeff >> 11) + (lp_coeff >> 12) + (lp_coeff >> 13) + (lp_coeff >> 14) + (lp_coeff >> 15) + (lp_coeff >> 16) ) >> 16;

    level_one_hp_coeffs.write(idx_one, hp_coeff_norm);
    level_one_lp_coeffs.write(idx_one, lp_coeff_norm);
    
    // keeps next computable index for level 1 (to avoid multiple executions)
    idx_one = idx_one + 1;
    level_one_index.write(0, idx_one);

    idx_zero = idx_zero + 2;
    next_level_zero_index.write(0, idx_zero);
  }

  action level_two() {
    // calculate element of first wavelet decomposition level
    bit<32> idx_one = 0;
    next_level_one_index.read(idx_one, 0);

    // bit<32> idx_two = (idx_one >> 1) - 1; // finds correct index of level 2 based on level 1
    bit<32> idx_two = 0;
    level_two_index.read(idx_two, 0);

    // number of points read depend on size of filter
    int<32> point_one = 0;
    int<32> point_two = 0;
    level_one_lp_coeffs.read(point_one, idx_one - 1);
    level_one_lp_coeffs.read(point_two, idx_one - 2);

    // simplified convolution of Haar wavelet coefficients, see notes for explanation
    int<32> hp_coeff = (point_one - point_two);
    int<32> lp_coeff = (point_two + point_one);
    
    // Normalization (division by sqrt(2) aproximation)
    int<32> hp_coeff_norm = (
      (hp_coeff << 15) + (hp_coeff << 13) + (hp_coeff << 12) + (hp_coeff << 10) + (hp_coeff <<  8) + (hp_coeff <<  2) + 
      (hp_coeff >>  1) + (hp_coeff >>  2) + (hp_coeff >>  3) + (hp_coeff >>  4) + (hp_coeff >>  7) + (hp_coeff >>  8) + 
      (hp_coeff >> 11) + (hp_coeff >> 12) + (hp_coeff >> 13) + (hp_coeff >> 14) + (hp_coeff >> 15) + (hp_coeff >> 16) ) >> 16;
    
    int<32> lp_coeff_norm = (
      (lp_coeff << 15) + (lp_coeff << 13) + (lp_coeff << 12) + (lp_coeff << 10) + (lp_coeff <<  8) + (lp_coeff <<  2) + 
      (lp_coeff >>  1) + (lp_coeff >>  2) + (lp_coeff >>  3) + (lp_coeff >>  4) + (lp_coeff >>  7) + (lp_coeff >>  8) + 
      (lp_coeff >> 11) + (lp_coeff >> 12) + (lp_coeff >> 13) + (lp_coeff >> 14) + (lp_coeff >> 15) + (lp_coeff >> 16) ) >> 16;

    level_two_hp_coeffs.write(idx_two, hp_coeff_norm);
    level_two_lp_coeffs.write(idx_two, lp_coeff_norm);

    // keeps next computable index for level 2 (to avoid multiple executions)
    idx_two = idx_two + 1;
    level_two_index.write(0, idx_two);

    idx_one = idx_one + 2;
    next_level_one_index.write(0, idx_one);
  }

  action level_three() {
    // calculate element of first wavelet decomposition level
    bit<32> idx_two = 0;
    next_level_two_index.read(idx_two, 0);

    // bit<32> idx_three = (idx_two >> 1) - 1; // finds correct index of level 3 based on level 2
    bit<32> idx_three = 0;
    level_three_index.read(idx_three, 0);

    // number of points read depend on size of filter
    int<32> point_one = 0;
    int<32> point_two = 0;
    level_two_lp_coeffs.read(point_one, idx_two - 1);
    level_two_lp_coeffs.read(point_two, idx_two - 2);

    // simplified convolution of Haar wavelet coefficients, see notes for explanation
    int<32> hp_coeff = (point_one - point_two);
    int<32> lp_coeff = (point_two + point_one);

    // Normalization (division by sqrt(2) aproximation)
    int<32> hp_coeff_norm = (
      (hp_coeff << 15) + (hp_coeff << 13) + (hp_coeff << 12) + (hp_coeff << 10) + (hp_coeff <<  8) + (hp_coeff <<  2) + 
      (hp_coeff >>  1) + (hp_coeff >>  2) + (hp_coeff >>  3) + (hp_coeff >>  4) + (hp_coeff >>  7) + (hp_coeff >>  8) + 
      (hp_coeff >> 11) + (hp_coeff >> 12) + (hp_coeff >> 13) + (hp_coeff >> 14) + (hp_coeff >> 15) + (hp_coeff >> 16) ) >> 16;
    
    int<32> lp_coeff_norm = (
      (lp_coeff << 15) + (lp_coeff << 13) + (lp_coeff << 12) + (lp_coeff << 10) + (lp_coeff <<  8) + (lp_coeff <<  2) + 
      (lp_coeff >>  1) + (lp_coeff >>  2) + (lp_coeff >>  3) + (lp_coeff >>  4) + (lp_coeff >>  7) + (lp_coeff >>  8) + 
      (lp_coeff >> 11) + (lp_coeff >> 12) + (lp_coeff >> 13) + (lp_coeff >> 14) + (lp_coeff >> 15) + (lp_coeff >> 16) ) >> 16;

    level_three_hp_coeffs.write(idx_three, hp_coeff_norm);
    level_three_lp_coeffs.write(idx_three, lp_coeff_norm);

    // keeps next computable index for level 3 (to avoid multiple executions)
    idx_three = idx_three + 1;
    level_three_index.write(0, idx_three);

    idx_two = idx_two + 2;
    next_level_two_index.write(0, idx_two);
  }

  action level_four() {
    // calculate element of first wavelet decomposition level
    bit<32> idx_three = 0;
    next_level_three_index.read(idx_three, 0);

    // bit<32> idx_four = (idx_three >> 1) - 1; // finds correct index of level 4 based on level 3
    bit<32> idx_four = 0;
    level_four_index.read(idx_four, 0);

    // number of points read depend on size of filter
    int<32> point_one = 0;
    int<32> point_two = 0;
    level_three_lp_coeffs.read(point_one, idx_three - 1);
    level_three_lp_coeffs.read(point_two, idx_three - 2);
    
    // simplified convolution of Haar wavelet coefficients, see notes for explanation
    int<32> hp_coeff = (point_one - point_two);
    int<32> lp_coeff = (point_two + point_one);

    // Normalization (division by sqrt(2) aproximation)
    int<32> hp_coeff_norm = (
      (hp_coeff << 15) + (hp_coeff << 13) + (hp_coeff << 12) + (hp_coeff << 10) + (hp_coeff <<  8) + (hp_coeff <<  2) + 
      (hp_coeff >>  1) + (hp_coeff >>  2) + (hp_coeff >>  3) + (hp_coeff >>  4) + (hp_coeff >>  7) + (hp_coeff >>  8) + 
      (hp_coeff >> 11) + (hp_coeff >> 12) + (hp_coeff >> 13) + (hp_coeff >> 14) + (hp_coeff >> 15) + (hp_coeff >> 16) ) >> 16;
    
    int<32> lp_coeff_norm = (
      (lp_coeff << 15) + (lp_coeff << 13) + (lp_coeff << 12) + (lp_coeff << 10) + (lp_coeff <<  8) + (lp_coeff <<  2) + 
      (lp_coeff >>  1) + (lp_coeff >>  2) + (lp_coeff >>  3) + (lp_coeff >>  4) + (lp_coeff >>  7) + (lp_coeff >>  8) + 
      (lp_coeff >> 11) + (lp_coeff >> 12) + (lp_coeff >> 13) + (lp_coeff >> 14) + (lp_coeff >> 15) + (lp_coeff >> 16) ) >> 16;

    level_four_hp_coeffs.write(idx_four, hp_coeff_norm);
    level_four_lp_coeffs.write(idx_four, lp_coeff_norm);

    // keeps next computable index for level 4 (to avoid multiple executions)
    idx_four = idx_four + 1;
    level_four_index.write(0, idx_four);

    idx_three = idx_three + 2;
    next_level_three_index.write(0,idx_three);
  }

  action level_five() {
    // calculate element of first wavelet decomposition level
    bit<32> idx_four = 0;
    next_level_four_index.read(idx_four, 0);

    // bit<32> idx_four = (idx_three >> 1) - 1; // finds correct index of level 4 based on level 3
    bit<32> idx_five = 0;
    level_five_index.read(idx_five, 0);

    // number of points read depend on size of filter
    int<32> point_one = 0;
    int<32> point_two = 0;
    level_four_lp_coeffs.read(point_one, idx_four - 1);
    level_four_lp_coeffs.read(point_two, idx_four - 2);
    
    // simplified convolution of Haar wavelet coefficients, see notes for explanation
    int<32> hp_coeff = (point_one - point_two);
    int<32> lp_coeff = (point_two + point_one);

    // Normalization (division by sqrt(2) aproximation)
    int<32> hp_coeff_norm = (
      (hp_coeff << 15) + (hp_coeff << 13) + (hp_coeff << 12) + (hp_coeff << 10) + (hp_coeff <<  8) + (hp_coeff <<  2) + 
      (hp_coeff >>  1) + (hp_coeff >>  2) + (hp_coeff >>  3) + (hp_coeff >>  4) + (hp_coeff >>  7) + (hp_coeff >>  8) + 
      (hp_coeff >> 11) + (hp_coeff >> 12) + (hp_coeff >> 13) + (hp_coeff >> 14) + (hp_coeff >> 15) + (hp_coeff >> 16) ) >> 16;
    
    int<32> lp_coeff_norm = (
      (lp_coeff << 15) + (lp_coeff << 13) + (lp_coeff << 12) + (lp_coeff << 10) + (lp_coeff <<  8) + (lp_coeff <<  2) + 
      (lp_coeff >>  1) + (lp_coeff >>  2) + (lp_coeff >>  3) + (lp_coeff >>  4) + (lp_coeff >>  7) + (lp_coeff >>  8) + 
      (lp_coeff >> 11) + (lp_coeff >> 12) + (lp_coeff >> 13) + (lp_coeff >> 14) + (lp_coeff >> 15) + (lp_coeff >> 16) ) >> 16;

    level_five_hp_coeffs.write(idx_five, hp_coeff_norm);
    level_five_lp_coeffs.write(idx_five, lp_coeff_norm);

    // keeps next computable index for level 4 (to avoid multiple executions)
    idx_five = idx_five + 1;
    level_five_index.write(0, idx_five);

    idx_four = idx_four + 2;
    next_level_four_index.write(0,idx_four);
  }

  action level_six() {
    // calculate element of first wavelet decomposition level
    bit<32> idx_five = 0;
    next_level_five_index.read(idx_five, 0);

    // bit<32> idx_five = (idx_three >> 1) - 1; // finds correct index of level 4 based on level 3
    bit<32> idx_six = 0;
    level_six_index.read(idx_six, 0);

    // number of points read depend on size of filter
    int<32> point_one = 0;
    int<32> point_two = 0;
    level_five_lp_coeffs.read(point_one, idx_five - 1);
    level_five_lp_coeffs.read(point_two, idx_five - 2);

    // simplified convolution of Haar wavelet coefficients, see notes for explanation
    int<32> hp_coeff = (point_one - point_two);
    int<32> lp_coeff = (point_two + point_one);

    // Normalization (division by sqrt(2) aproximation)
    int<32> hp_coeff_norm = (
      (hp_coeff << 15) + (hp_coeff << 13) + (hp_coeff << 12) + (hp_coeff << 10) + (hp_coeff <<  8) + (hp_coeff <<  2) + 
      (hp_coeff >>  1) + (hp_coeff >>  2) + (hp_coeff >>  3) + (hp_coeff >>  4) + (hp_coeff >>  7) + (hp_coeff >>  8) + 
      (hp_coeff >> 11) + (hp_coeff >> 12) + (hp_coeff >> 13) + (hp_coeff >> 14) + (hp_coeff >> 15) + (hp_coeff >> 16) ) >> 16;
    
    int<32> lp_coeff_norm = (
      (lp_coeff << 15) + (lp_coeff << 13) + (lp_coeff << 12) + (lp_coeff << 10) + (lp_coeff <<  8) + (lp_coeff <<  2) + 
      (lp_coeff >>  1) + (lp_coeff >>  2) + (lp_coeff >>  3) + (lp_coeff >>  4) + (lp_coeff >>  7) + (lp_coeff >>  8) + 
      (lp_coeff >> 11) + (lp_coeff >> 12) + (lp_coeff >> 13) + (lp_coeff >> 14) + (lp_coeff >> 15) + (lp_coeff >> 16) ) >> 16;

    level_six_hp_coeffs.write(idx_six, hp_coeff_norm);
    level_six_lp_coeffs.write(idx_six, lp_coeff_norm);

    // keeps next computable index for level 4 (to avoid multiple executions)
    idx_six = idx_six + 1;
    level_six_index.write(0, idx_six);

    idx_five = idx_five + 2;
    next_level_five_index.write(0,idx_five);
  }

  action level_seven() {
    // calculate element of first wavelet decomposition level
    bit<32> idx_six = 0;
    next_level_six_index.read(idx_six, 0);

    // bit<32> idx_six = (idx_three >> 1) - 1; // finds correct index of level 4 based on level 3
    bit<32> idx_seven = 0;
    level_seven_index.read(idx_seven, 0);

    // number of points read depend on size of filter
    int<32> point_one = 0;
    int<32> point_two = 0;
    level_six_lp_coeffs.read(point_one, idx_six - 1);
    level_six_lp_coeffs.read(point_two, idx_six - 2);
    
    // simplified convolution of Haar wavelet coefficients, see notes for explanation
    int<32> hp_coeff = (point_one - point_two);
    int<32> lp_coeff = (point_two + point_one);

    // Normalization (division by sqrt(2) aproximation)
    int<32> hp_coeff_norm = (
      (hp_coeff << 15) + (hp_coeff << 13) + (hp_coeff << 12) + (hp_coeff << 10) + (hp_coeff <<  8) + (hp_coeff <<  2) + 
      (hp_coeff >>  1) + (hp_coeff >>  2) + (hp_coeff >>  3) + (hp_coeff >>  4) + (hp_coeff >>  7) + (hp_coeff >>  8) + 
      (hp_coeff >> 11) + (hp_coeff >> 12) + (hp_coeff >> 13) + (hp_coeff >> 14) + (hp_coeff >> 15) + (hp_coeff >> 16) ) >> 16;
    
    int<32> lp_coeff_norm = (
      (lp_coeff << 15) + (lp_coeff << 13) + (lp_coeff << 12) + (lp_coeff << 10) + (lp_coeff <<  8) + (lp_coeff <<  2) + 
      (lp_coeff >>  1) + (lp_coeff >>  2) + (lp_coeff >>  3) + (lp_coeff >>  4) + (lp_coeff >>  7) + (lp_coeff >>  8) + 
      (lp_coeff >> 11) + (lp_coeff >> 12) + (lp_coeff >> 13) + (lp_coeff >> 14) + (lp_coeff >> 15) + (lp_coeff >> 16) ) >> 16;

    level_seven_hp_coeffs.write(idx_seven, hp_coeff_norm);
    level_seven_lp_coeffs.write(idx_seven, lp_coeff_norm);

    // keeps next computable index for level 4 (to avoid multiple executions)
    idx_seven = idx_seven + 1;
    level_seven_index.write(0, idx_seven);

    idx_six = idx_six + 2;
    next_level_six_index.write(0,idx_six);
  }

  action level_eight() {
    // calculate element of first wavelet decomposition level
    bit<32> idx_seven = 0;
    next_level_seven_index.read(idx_seven, 0);

    // bit<32> idx_seven = (idx_three >> 1) - 1; // finds correct index of level 4 based on level 3
    bit<32> idx_eight = 0;
    level_eight_index.read(idx_eight, 0);

    // number of points read depend on size of filter
    int<32> point_one = 0;
    int<32> point_two = 0;
    level_seven_lp_coeffs.read(point_one, idx_seven - 1);
    level_seven_lp_coeffs.read(point_two, idx_seven - 2);
    
    // simplified convolution of Haar wavelet coefficients, see notes for explanation
    int<32> hp_coeff = (point_one - point_two);
    int<32> lp_coeff = (point_two + point_one);

    // Normalization (division by sqrt(2) aproximation)
    int<32> hp_coeff_norm = (
      (hp_coeff << 15) + (hp_coeff << 13) + (hp_coeff << 12) + (hp_coeff << 10) + (hp_coeff <<  8) + (hp_coeff <<  2) + 
      (hp_coeff >>  1) + (hp_coeff >>  2) + (hp_coeff >>  3) + (hp_coeff >>  4) + (hp_coeff >>  7) + (hp_coeff >>  8) + 
      (hp_coeff >> 11) + (hp_coeff >> 12) + (hp_coeff >> 13) + (hp_coeff >> 14) + (hp_coeff >> 15) + (hp_coeff >> 16) ) >> 16;
    
    int<32> lp_coeff_norm = (
      (lp_coeff << 15) + (lp_coeff << 13) + (lp_coeff << 12) + (lp_coeff << 10) + (lp_coeff <<  8) + (lp_coeff <<  2) + 
      (lp_coeff >>  1) + (lp_coeff >>  2) + (lp_coeff >>  3) + (lp_coeff >>  4) + (lp_coeff >>  7) + (lp_coeff >>  8) + 
      (lp_coeff >> 11) + (lp_coeff >> 12) + (lp_coeff >> 13) + (lp_coeff >> 14) + (lp_coeff >> 15) + (lp_coeff >> 16) ) >> 16;

    level_eight_hp_coeffs.write(idx_eight, hp_coeff_norm);
    level_eight_lp_coeffs.write(idx_eight, lp_coeff_norm);

    // keeps next computable index for level 4 (to avoid multiple executions)
    idx_eight = idx_eight + 1;
    level_eight_index.write(0, idx_eight);

    idx_seven = idx_seven + 2;
    next_level_seven_index.write(0,idx_seven);
  }


  apply {
    bit<32> offset = 0;
    bit<32> iter_signal = 0;
    bit<48> value_ingress_timestamp = 0;
    bit<48> value_timestamp = 0;
    bit<32> index = 0;
    int<32> count = 0;

    value_timestamp = standard_metadata.ingress_global_timestamp;
    // value_ingress_timestamp = division_micro(value_timestamp);
    value_ingress_timestamp = division_48(value_timestamp, 1000000);
    // TODO: divide by 10^6 instead of 2^20
    bit<32> ingress_time_in_seconds = (bit<32>) (value_ingress_timestamp); // division by 2^20 (~10^6)
    timestamp_offset.read(offset, 0);

    // count the incoming packets
    count_signal.read(iter_signal, 0);
    iter_signal = iter_signal + 1;
    count_signal.write(0, iter_signal);

    // Get timestamp value and division value
    values_division.write(iter_signal << 1, value_timestamp);
    values_division.write((iter_signal << 1) + 1, value_ingress_timestamp);    

    values_global_timestamp.write(iter_signal, ingress_time_in_seconds);
    values_offset.write(iter_signal, offset);

    // check if offset for timestamps has been initialized and
    // check if index is larger than register size, and reset offset if so
    if (offset == 0 || index >= SIGNAL_SIZE) {
      // TODO: clear entire signal register, and coefficients registers
      index = 0;
      offset = ingress_time_in_seconds;
      timestamp_offset.write(0, offset);
      next_level_zero_index.write(0, 2);
      next_level_one_index.write(0, 2);
      next_level_two_index.write(0, 2);
      next_level_three_index.write(0, 2);
      next_level_four_index.write(0, 2);
      next_level_five_index.write(0, 2);
      next_level_six_index.write(0, 2);
      next_level_seven_index.write(0, 2);
      // next_level_eight_index.write(0, 2);
      // next_level_nine_index.write(0, 2);
    }

    // get index of incoming packet timestamp in seconds
    index = ingress_time_in_seconds - offset;
    // get values of index by packet
    values_index.write(iter_signal, index);
    
    /* increment signal count for the current second */
    signal.read(count, index);
    count = count + 10;
    signal.write(index, count);
    signal_index.write(0, index);

    /* ***************** LEVEL 1 ********************* */
    bit<32> idx_one = 0;
    bit<32> nxt_idx_zero = 0;
    level_one_index.read(idx_one, 0);
    next_level_zero_index.read(nxt_idx_zero, 0);
    /* if there's enough data to calculate level one (lvl zero index is two positions ahead of lvl one) */
    if (index >= nxt_idx_zero) {
    // if ((index >> 1) > idx_one) {
      level_one();
      level_one_index.read(idx_one, 0);
      // idx_one = nxt_idx_zero >> 1; // correct index for later checks without re-reading register

      // read last level one lp coeff to compute square 
      int<32> lp_coeff = 0;
      int<32> hp_coeff = 0;
      level_one_lp_coeffs.read(lp_coeff, idx_one - 1);
      level_one_hp_coeffs.read(hp_coeff, idx_one - 1);
      squared.apply(lp_coeff, hp_coeff, 1, idx_one - 1);
    }
    // values_level_one_index.write(iter_signal, idx_one);

    /* ***************** LEVEL 2 ********************* */
    bit<32> idx_two = 0;
    bit<32> nxt_idx_one = 0;
    level_two_index.read(idx_two, 0);
    next_level_one_index.read(nxt_idx_one, 0);
    /* if there's enough data to calculate level two (lvl one index is two positions ahead of lvl two) */
    if (idx_one >= nxt_idx_one) {
      level_two();
      level_two_index.read(idx_two, 0);
      // idx_two = nxt_idx_one >> 1; // correct index for later checks without re-reading register

       // read last level two lp coeff to compute square 
      int<32> lp_coeff = 0;
      int<32> hp_coeff = 0;
      level_two_lp_coeffs.read(lp_coeff, idx_two - 1);
      level_two_hp_coeffs.read(hp_coeff, idx_two - 1);
      squared.apply(lp_coeff, hp_coeff, 2, idx_two - 1);
    }
    // values_level_two_index.write(iter_signal, idx_two);

    /* ***************** LEVEL 3 ********************* */
    bit<32> idx_three = 0;
    bit<32> nxt_idx_two = 0;
    level_three_index.read(idx_three, 0);
    next_level_two_index.read(nxt_idx_two, 0);
    /* if there's enough data to calculate level three (lvl two index is two positions ahead of lvl three) */
    if (idx_two >= nxt_idx_two) {
    // if ((idx_two >> 1) > idx_three) {
      level_three();
      level_three_index.read(idx_three, 0);
      // idx_three = nxt_idx_two >> 1; // correct index for later checks without re-reading register

       // read last level three lp coeff to compute square 
      int<32> lp_coeff = 0;
      int<32> hp_coeff = 0;
      level_three_lp_coeffs.read(lp_coeff, idx_three - 1);
      level_three_hp_coeffs.read(hp_coeff, idx_three - 1);
      squared.apply(lp_coeff, hp_coeff, 3, idx_three - 1);
    }
    // values_level_three_index.write(iter_signal, idx_three);

    /* ***************** LEVEL 4 ********************* */
    bit<32> idx_four = 0;
    bit<32> nxt_idx_three = 0;
    level_four_index.read(idx_four, 0);
    next_level_three_index.read(nxt_idx_three, 0);
    /* if there's enough data to calculate level four (lvl three index is two positions ahead of lvl four) */
    if (idx_three >= nxt_idx_three) {
    // if ((idx_three >> 1) > idx_four) {
      level_four();
      level_four_index.read(idx_four, 0);
      // idx_four = nxt_idx_three >> 1; // correct index for later checks without re-reading register

       // read last level four lp coeff to compute square 
      int<32> lp_coeff = 0;
      int<32> hp_coeff = 0;
      level_four_lp_coeffs.read(lp_coeff, idx_four - 1);
      level_four_hp_coeffs.read(hp_coeff, idx_four - 1);
      squared.apply(lp_coeff, hp_coeff, 4, idx_four - 1);
    }
    // values_level_four_index.write(iter_signal, idx_four);

    /* ***************** LEVEL 5 ********************* */
    bit<32> idx_five = 0;
    bit<32> nxt_idx_four = 0;
    level_five_index.read(idx_five, 0);
    next_level_four_index.read(nxt_idx_four, 0);
    /* if there's enough data to calculate level five (lvl four index is two positions ahead of lvl five) */
    if (idx_four >= nxt_idx_four) {
    // if ((idx_four >> 1) > idx_five) {
      level_five();
      level_five_index.read(idx_five, 0);
      // idx_five = nxt_idx_four >> 1; // correct index for later checks without re-reading register

       // read last level five lp coeff to compute square 
      int<32> lp_coeff = 0;
      int<32> hp_coeff = 0;
      level_five_lp_coeffs.read(lp_coeff, idx_five - 1);
      level_five_hp_coeffs.read(hp_coeff, idx_five - 1);
      squared.apply(lp_coeff, hp_coeff, 5, idx_five - 1);
    }
    // values_level_five_index.write(iter_signal, idx_five);

    /* ***************** LEVEL 6 ********************* */
    bit<32> idx_six = 0;
    bit<32> nxt_idx_five = 0;
    level_six_index.read(idx_six, 0);
    next_level_five_index.read(nxt_idx_five, 0);
    /* if there's enough data to calculate level six (lvl five index is two positions ahead of lvl six) */
    if (idx_five >= nxt_idx_five) {
    // if ((idx_five >> 1) > idx_six) {
      level_six();
      level_six_index.read(idx_six, 0);
      // idx_six = nxt_idx_five >> 1; // correct index for later checks without re-reading register

       // read last level six lp coeff to compute square 
      int<32> lp_coeff = 0;
      int<32> hp_coeff = 0;
      level_six_lp_coeffs.read(lp_coeff, idx_six - 1);
      level_six_hp_coeffs.read(hp_coeff, idx_six - 1);
      squared.apply(lp_coeff, hp_coeff, 6, idx_six - 1);
    }
    // values_level_six_index.write(iter_signal, idx_six);

    /* ***************** LEVEL 7 ********************* */
    bit<32> idx_seven = 0;
    bit<32> nxt_idx_six = 0;
    level_seven_index.read(idx_seven, 0);
    next_level_six_index.read(nxt_idx_six, 0);
    /* if there's enough data to calculate level seven (lvl six index is two positions ahead of lvl seven) */
    if (idx_six >= nxt_idx_six) {
    // if ((idx_six >> 1) > idx_seven) {
      level_seven();
      level_seven_index.read(idx_seven, 0);
      // idx_seven = nxt_idx_six >> 1; // correct index for later checks without re-reading register

       // read last level seven lp coeff to compute square 
      int<32> lp_coeff = 0;
      int<32> hp_coeff = 0;
      level_seven_lp_coeffs.read(lp_coeff, idx_seven - 1);
      level_seven_hp_coeffs.read(hp_coeff, idx_seven - 1);
      squared.apply(lp_coeff, hp_coeff, 7, idx_seven - 1);
    }
    // values_level_seven_index.write(iter_signal, idx_seven);

    /* ***************** LEVEL 8 ********************* */
    bit<32> idx_eight = 0;
    bit<32> nxt_idx_seven = 0;
    level_eight_index.read(idx_eight, 0);
    next_level_seven_index.read(nxt_idx_seven, 0);
    /* if there's enough data to calculate level eight (lvl seven index is two positions ahead of lvl eight) */
    if (idx_seven >= nxt_idx_seven) {
    // if ((idx_seven >> 1) > idx_eight) {
      level_eight();
      level_eight_index.read(idx_eight, 0);
      // idx_eight = nxt_idx_seven >> 1; // correct index for later checks without re-reading register

       // read last level eight lp coeff to compute square 
      int<32> lp_coeff = 0;
      int<32> hp_coeff = 0;
      level_eight_lp_coeffs.read(lp_coeff, idx_eight - 1);
      level_eight_hp_coeffs.read(hp_coeff, idx_eight - 1);
      squared.apply(lp_coeff, hp_coeff, 8, idx_eight - 1);
    }
    // values_level_eight_index.write(iter_signal, idx_eight);

  }
}

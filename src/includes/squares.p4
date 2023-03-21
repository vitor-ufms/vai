/* -*- P4_16 -*- */
/* P4 program for calculating sum of squares */
/* Arthur Selle Jacobs (asjacobs@inf.ufrgs.br) */
/* INF-UFRGS / Princeton University Computer Science Department */
/* Briggette Roman Huaytalla (borhuaytalla@inf.ufrgs.br) */
/* INF-UFRGS */

/* number of decomposition levels of the wavelet transform */
#define NUM_LEVELS 10
#define SIGNAL_SIZE 3072

/*structure for division values */
struct div
{
  bit<48> dividend;
  bit<48> quotient;
};
typedef div Div;

/*************************************************************************
*********************** R E G I S T E R S  *****************************
*************************************************************************/

/* registers for sum of squares  */
register<bit<48>>(NUM_LEVELS + 1) lst_sum_lp;
register<bit<48>>(NUM_LEVELS + 1) sum_of_squares_lp;
register<bit<48>>(NUM_LEVELS + 1) variance_lp;

register<bit<48>>(NUM_LEVELS + 1) lst_sum_hp;
register<bit<48>>(NUM_LEVELS + 1) sum_of_squares_hp;
register<bit<48>>(NUM_LEVELS + 1) variance_hp;

/* for debugging */
register<bit<48>>(SIGNAL_SIZE / 2) level_one_lp_squares;
register<bit<48>>(SIGNAL_SIZE / 4) level_two_lp_squares;
register<bit<48>>(SIGNAL_SIZE / 8) level_three_lp_squares;
register<bit<48>>(SIGNAL_SIZE / 16) level_four_lp_squares;
register<bit<48>>(SIGNAL_SIZE / 32) level_five_lp_squares;
register<bit<48>>(SIGNAL_SIZE / 64) level_six_lp_squares;
register<bit<48>>(SIGNAL_SIZE / 128) level_seven_lp_squares;
register<bit<48>>(SIGNAL_SIZE / 256) level_eight_lp_squares;
register<bit<48>>(SIGNAL_SIZE / 512) level_nine_lp_squares;
register<bit<48>>(SIGNAL_SIZE / 1024) level_ten_lp_squares;

register<bit<48>>(SIGNAL_SIZE / 2) level_one_hp_squares;
register<bit<48>>(SIGNAL_SIZE / 4) level_two_hp_squares;
register<bit<48>>(SIGNAL_SIZE / 8) level_three_hp_squares;
register<bit<48>>(SIGNAL_SIZE / 16) level_four_hp_squares;
register<bit<48>>(SIGNAL_SIZE / 32) level_five_hp_squares;
register<bit<48>>(SIGNAL_SIZE / 64) level_six_hp_squares;
register<bit<48>>(SIGNAL_SIZE / 128) level_seven_hp_squares;
register<bit<48>>(SIGNAL_SIZE / 256) level_eight_hp_squares;
register<bit<48>>(SIGNAL_SIZE / 512) level_nine_hp_squares;
register<bit<48>>(SIGNAL_SIZE / 1024) level_ten_hp_squares;


register<bit<48>>(SIGNAL_SIZE / 2) level_one_lp_variance;
register<bit<48>>(SIGNAL_SIZE / 4) level_two_lp_variance;
register<bit<48>>(SIGNAL_SIZE / 8) level_three_lp_variance;
register<bit<48>>(SIGNAL_SIZE / 16) level_four_lp_variance;
register<bit<48>>(SIGNAL_SIZE / 32) level_five_lp_variance;
register<bit<48>>(SIGNAL_SIZE / 64) level_six_lp_variance;
register<bit<48>>(SIGNAL_SIZE / 128) level_seven_lp_variance;
register<bit<48>>(SIGNAL_SIZE / 256) level_eight_lp_variance;
register<bit<48>>(SIGNAL_SIZE / 512) level_nine_lp_variance;
register<bit<48>>(SIGNAL_SIZE / 1024) level_ten_lp_variance;

register<bit<48>>(SIGNAL_SIZE / 2) level_one_hp_variance;
register<bit<48>>(SIGNAL_SIZE / 4) level_two_hp_variance;
register<bit<48>>(SIGNAL_SIZE / 8) level_three_hp_variance;
register<bit<48>>(SIGNAL_SIZE / 16) level_four_hp_variance;
register<bit<48>>(SIGNAL_SIZE / 32) level_five_hp_variance;
register<bit<48>>(SIGNAL_SIZE / 64) level_six_hp_variance;
register<bit<48>>(SIGNAL_SIZE / 128) level_seven_hp_variance;
register<bit<48>>(SIGNAL_SIZE / 256) level_eight_hp_variance;
register<bit<48>>(SIGNAL_SIZE / 512) level_nine_hp_variance;
register<bit<48>>(SIGNAL_SIZE / 1024) level_ten_hp_variance;

bit<32> abs(in int<32> num) {
  bit<32> result = (bit<32>) num;
  bit<32> mask = (1 << 31);
  if (result & mask != 0) {
    result = (~result) + 1;
  } 

  return result;
}

bit<48> abs_48(in int<48> num) {
  bit<48> result = (bit<48>) num;
  bit<48> mask = (1 << 47);
  if (result & mask != 0) {
    result = (~result) + 1;
  } 

  return result;
}

bit<32> sqrt2div_32 (in int<32> num) {
  bit <32> result = (bit<32>) num;

  result = (
		(result << 15) + (result << 13) + (result << 12) + (result << 10) + (result <<  8) + (result <<  2) + 
		(result >>  1) + (result >>  2) + (result >>  3) + (result >>  4) + (result >>  7) + (result >>  8) + 
		(result >> 11) + (result >> 12) + (result >> 13) + (result >> 14) + (result >> 15) + (result >> 16) ) >> 16;

  return result;
}

bit<32> square_step(in bit<32> val, in bit<32> result, in bit<32> mask) {
  bit<32> sum = result;
  if (val & mask != 0) {
    sum = sum + val;
  }
  if (mask != 1) {
    sum = sum << 1;
  }
  return sum;
}

bit<48> square_step_48(in bit<48> val, in bit<48> result, in bit<48> mask) {
  bit<48> sum = result;
  if (val & mask != 0) {
    sum = sum + val;
  }
  if (mask != 1) {
    sum = sum << 1;
  }
  return sum;
}

bit<32> square(in int<32> num) {
  bit<32> result = 0;
  bit<32> val = abs(num);

  // for 32 bit numbers
  result = square_step(val, result, 1 << 31);
  result = square_step(val, result, 1 << 30);
  result = square_step(val, result, 1 << 29);
  result = square_step(val, result, 1 << 28);
  result = square_step(val, result, 1 << 27);
  result = square_step(val, result, 1 << 26);
  result = square_step(val, result, 1 << 25);
  result = square_step(val, result, 1 << 24);
  result = square_step(val, result, 1 << 23);
  result = square_step(val, result, 1 << 22);
  result = square_step(val, result, 1 << 21);
  result = square_step(val, result, 1 << 20);
  result = square_step(val, result, 1 << 19);
  result = square_step(val, result, 1 << 18);
  result = square_step(val, result, 1 << 17);
  result = square_step(val, result, 1 << 16);
  result = square_step(val, result, 1 << 15);
  result = square_step(val, result, 1 << 14);
  result = square_step(val, result, 1 << 13);
  result = square_step(val, result, 1 << 12);
  result = square_step(val, result, 1 << 11);
  result = square_step(val, result, 1 << 10);
  result = square_step(val, result, 1 << 9);
  result = square_step(val, result, 1 << 8);
  result = square_step(val, result, 1 << 7);
  result = square_step(val, result, 1 << 6);
  result = square_step(val, result, 1 << 5);
  result = square_step(val, result, 1 << 4);
  result = square_step(val, result, 1 << 3);
  result = square_step(val, result, 1 << 2);
  result = square_step(val, result, 1 << 1);
  result = square_step(val, result, 1);

  return result;
}

bit<48> square_48(in int<48> num) {
  bit<48> result = 0;
  bit<48> val = abs_48(num);

  // for 48 bit numbers
  result = square_step_48(val, result, 1 << 47);
  result = square_step_48(val, result, 1 << 46);
  result = square_step_48(val, result, 1 << 45);
  result = square_step_48(val, result, 1 << 44);
  result = square_step_48(val, result, 1 << 43);
  result = square_step_48(val, result, 1 << 42);
  result = square_step_48(val, result, 1 << 41);
  result = square_step_48(val, result, 1 << 40);
  result = square_step_48(val, result, 1 << 39);
  result = square_step_48(val, result, 1 << 38);
  result = square_step_48(val, result, 1 << 37);
  result = square_step_48(val, result, 1 << 36);
  result = square_step_48(val, result, 1 << 35);
  result = square_step_48(val, result, 1 << 34);
  result = square_step_48(val, result, 1 << 33);
  result = square_step_48(val, result, 1 << 32);
  result = square_step_48(val, result, 1 << 31);
  result = square_step_48(val, result, 1 << 30);
  result = square_step_48(val, result, 1 << 29);
  result = square_step_48(val, result, 1 << 28);
  result = square_step_48(val, result, 1 << 27);
  result = square_step_48(val, result, 1 << 26);
  result = square_step_48(val, result, 1 << 25);
  result = square_step_48(val, result, 1 << 24);
  result = square_step_48(val, result, 1 << 23);
  result = square_step_48(val, result, 1 << 22);
  result = square_step_48(val, result, 1 << 21);
  result = square_step_48(val, result, 1 << 20);
  result = square_step_48(val, result, 1 << 19);
  result = square_step_48(val, result, 1 << 18);
  result = square_step_48(val, result, 1 << 17);
  result = square_step_48(val, result, 1 << 16);
  result = square_step_48(val, result, 1 << 15);
  result = square_step_48(val, result, 1 << 14);
  result = square_step_48(val, result, 1 << 13);
  result = square_step_48(val, result, 1 << 12);
  result = square_step_48(val, result, 1 << 11);
  result = square_step_48(val, result, 1 << 10);
  result = square_step_48(val, result, 1 << 9);
  result = square_step_48(val, result, 1 << 8);
  result = square_step_48(val, result, 1 << 7);
  result = square_step_48(val, result, 1 << 6);
  result = square_step_48(val, result, 1 << 5);
  result = square_step_48(val, result, 1 << 4);
  result = square_step_48(val, result, 1 << 3);
  result = square_step_48(val, result, 1 << 2);
  result = square_step_48(val, result, 1 << 1);
  result = square_step_48(val, result, 1);

  return result;
}

Div divide_step(in bit<48> divisor, in Div value, in int<8> position ){

  Div val; 
  val.dividend = value.dividend;
  val.quotient = value.quotient; 
  bit<8> pos = (bit<8>)position;
  if(position >= 0){
      // Update if divisor =< Dividend
    if(val.dividend >= divisor){
      bit<48> amount = 1 << (bit<8>)position;
      val.quotient = val.quotient + amount;
      val.dividend = val.dividend - divisor;
    }
  }
  // Return the update values
  return val;
}

/************************************************************************
********************** DIVISION FOR 32-BIT NUMBERS **********************
*************************************************************************/


bit<32> division_32(in bit<32> dividnd, in bit<32> divisr) {

  bit<48> divisor = (bit<48>) divisr;
  // Set de value of Dividend and Quotient
  Div value;
  value.dividend = (bit<48>) dividnd;
  value.quotient = 0;
  // Start in the position 0 for align
  int<8> position = 0;
  if (divisor == 0) {return (bit<32>) 0;}

  // Set position and align the divisor
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}

  // Calculate quotient
  value = divide_step(divisor >> 1, value, position - 1);
  value = divide_step(divisor >> 2, value, position - 2);
  value = divide_step(divisor >> 3, value, position - 3);
  value = divide_step(divisor >> 4, value, position - 4);
  value = divide_step(divisor >> 5, value, position - 5);
  value = divide_step(divisor >> 6, value, position - 6);
  value = divide_step(divisor >> 7, value, position - 7);
  value = divide_step(divisor >> 8, value, position - 8);
  value = divide_step(divisor >> 9, value, position - 9);
  value = divide_step(divisor >> 10, value, position - 10);
  value = divide_step(divisor >> 11, value, position - 11);
  value = divide_step(divisor >> 12, value, position - 12);
  value = divide_step(divisor >> 13, value, position - 13);
  value = divide_step(divisor >> 14, value, position - 14);
  value = divide_step(divisor >> 15, value, position - 15);
  value = divide_step(divisor >> 16, value, position - 16);
  value = divide_step(divisor >> 17, value, position - 17);
  value = divide_step(divisor >> 18, value, position - 18);
  value = divide_step(divisor >> 19, value, position - 19);
  value = divide_step(divisor >> 20, value, position - 20);
  value = divide_step(divisor >> 21, value, position - 21);
  value = divide_step(divisor >> 22, value, position - 22);
  value = divide_step(divisor >> 23, value, position - 23);
  value = divide_step(divisor >> 24, value, position - 24);
  value = divide_step(divisor >> 25, value, position - 25);
  value = divide_step(divisor >> 26, value, position - 26);
  value = divide_step(divisor >> 27, value, position - 27);
  value = divide_step(divisor >> 28, value, position - 28);
  value = divide_step(divisor >> 29, value, position - 29);
  value = divide_step(divisor >> 30, value, position - 30);
  value = divide_step(divisor >> 31, value, position - 31);

  return (bit <32>)value.quotient;
}


bit<48> division_48(in bit<48> dividnd, in bit<48> divisr) {

  bit<48> divisor = divisr;
  // Set de value of Dividend and Quotient
  Div value;
  value.dividend = dividnd;
  value.quotient = 0;
  // Start in the position 0 for align
  int<8> position = 0;

  if (divisor == 0) {return (bit<48>) 0;}

  // Extract the to need align
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}
  if(divisor < value.dividend){ position = position + 1; divisor = divisor << 1;}

  // Calculate quotient
  value = divide_step(divisor >> 1, value, position - 1);
  value = divide_step(divisor >> 2, value, position - 2);
  value = divide_step(divisor >> 3, value, position - 3);
  value = divide_step(divisor >> 4, value, position - 4);
  value = divide_step(divisor >> 5, value, position - 5);
  value = divide_step(divisor >> 6, value, position - 6);
  value = divide_step(divisor >> 7, value, position - 7);
  value = divide_step(divisor >> 8, value, position - 8);
  value = divide_step(divisor >> 9, value, position - 9);
  value = divide_step(divisor >> 10, value, position - 10);
  value = divide_step(divisor >> 11, value, position - 11);
  value = divide_step(divisor >> 12, value, position - 12);
  value = divide_step(divisor >> 13, value, position - 13);
  value = divide_step(divisor >> 14, value, position - 14);
  value = divide_step(divisor >> 15, value, position - 15);
  value = divide_step(divisor >> 16, value, position - 16);
  value = divide_step(divisor >> 17, value, position - 17);
  value = divide_step(divisor >> 18, value, position - 18);
  value = divide_step(divisor >> 19, value, position - 19);
  value = divide_step(divisor >> 20, value, position - 20);
  value = divide_step(divisor >> 21, value, position - 21);
  value = divide_step(divisor >> 22, value, position - 22);
  value = divide_step(divisor >> 23, value, position - 23);
  value = divide_step(divisor >> 24, value, position - 24);
  value = divide_step(divisor >> 25, value, position - 25);
  value = divide_step(divisor >> 26, value, position - 26);
  value = divide_step(divisor >> 27, value, position - 27);
  value = divide_step(divisor >> 28, value, position - 28);
  value = divide_step(divisor >> 29, value, position - 29);
  value = divide_step(divisor >> 30, value, position - 30);
  value = divide_step(divisor >> 31, value, position - 31);
  value = divide_step(divisor >> 32, value, position - 32);
  value = divide_step(divisor >> 33, value, position - 33);
  value = divide_step(divisor >> 34, value, position - 34);
  value = divide_step(divisor >> 35, value, position - 35);
  value = divide_step(divisor >> 36, value, position - 36);
  value = divide_step(divisor >> 37, value, position - 37);
  value = divide_step(divisor >> 38, value, position - 38);
  value = divide_step(divisor >> 39, value, position - 39);
  value = divide_step(divisor >> 40, value, position - 40);
  value = divide_step(divisor >> 41, value, position - 41);
  value = divide_step(divisor >> 42, value, position - 42);
  value = divide_step(divisor >> 43, value, position - 43);
  value = divide_step(divisor >> 44, value, position - 44);
  value = divide_step(divisor >> 45, value, position - 45);
  value = divide_step(divisor >> 46, value, position - 46);
  value = divide_step(divisor >> 47, value, position - 47);

  return value.quotient;
}

/************************************************************************
************************** DIVISION by 1000000 **************************
*************************************************************************/

bit<48> division_micro(in bit<48> dividnd){
  bit<48> quotient = 0;
  bit<48> remainder = 0;

  // Division by 10
  quotient = (dividnd >> 1) + (dividnd >> 2);
  quotient = quotient + (quotient >> 4);
  quotient = quotient + (quotient >> 8); 
  quotient = quotient >> 3;
  remainder = dividnd - (((quotient << 2) + quotient) << 1);
  if (remainder > 9) { quotient = quotient + 1;}
  // Division by 100
  quotient = (quotient >> 1) + (quotient >> 2);
  quotient = quotient + (quotient >> 4);
  quotient = quotient + (quotient >> 8); 
  quotient = quotient >> 3;
  remainder = dividnd - (((quotient << 2) + quotient) << 1);
  if (remainder > 9) { quotient = quotient + 1;}
  // Division by 1000
  quotient = (quotient >> 1) + (quotient >> 2);
  quotient = quotient + (quotient >> 4);
  quotient = quotient + (quotient >> 8); 
  quotient = quotient >> 3;
  remainder = dividnd - (((quotient << 2) + quotient) << 1);
  if (remainder > 9) { quotient = quotient + 1;}
  // Division by 10000
  quotient = (quotient >> 1) + (quotient >> 2);
  quotient = quotient + (quotient >> 4);
  quotient = quotient + (quotient >> 8); 
  quotient = quotient >> 3;
  remainder = dividnd - (((quotient << 2) + quotient) << 1);
  if (remainder > 9) { quotient = quotient + 1;}
  // Division by 100000
  quotient = (quotient >> 1) + (quotient >> 2);
  quotient = quotient + (quotient >> 4);
  quotient = quotient + (quotient >> 8); 
  quotient = quotient >> 3;
  remainder = dividnd - (((quotient << 2) + quotient) << 1);
  if (remainder > 9) { quotient = quotient + 1;}
  // Division by 1000000
  quotient = (quotient >> 1) + (quotient >> 2);
  quotient = quotient + (quotient >> 4);
  quotient = quotient + (quotient >> 8); 
  quotient = quotient >> 3;
  remainder = dividnd - (((quotient << 2) + quotient) << 1);
  // if (remainder > 9) { quotient = quotient + 1;}

  return quotient;
}

/************************************************************************
********** S U M  O F  S Q U A R E S  P R O C E S S I N G ***************
*************************************************************************/
control SumOfSquares(in int<32> number_lp, in int<32> number_hp, in bit<32> level, in bit<32> index) {
  apply {


    bit<48> squared_sum_lp = 0;
    bit<48> sum_lp = 0; 
    bit<48> sum_squares_lp = 0; 
    bit<48> var_lp = 0;
    bit<32> coeff_lp = 0;
    bit<48> division_result_lp = 0;
    bit<48> squared_num_lp = square_48((int<48>) number_lp);


    coeff_lp =  (bit <32>) number_lp;
    lst_sum_lp.read(sum_lp, level);
    sum_lp = sum_lp + (bit<48>) coeff_lp;
    lst_sum_lp.write(level, sum_lp);

    sum_of_squares_lp.read(sum_squares_lp, level);
    sum_squares_lp = sum_squares_lp + squared_num_lp; 
    sum_of_squares_lp.write(level, sum_squares_lp);

    squared_sum_lp = square_48((int<48>) sum_lp);
    division_result_lp = division_48(squared_sum_lp, (bit<48>)index + 1);
    squared_sum_lp = division_result_lp;
    var_lp = sum_squares_lp - squared_sum_lp;
    division_result_lp = division_48(var_lp, (bit<48>)index);
    var_lp = division_result_lp;
    variance_lp.write(level, var_lp);
    

    bit<48> squared_sum_hp = 0;
    bit<48> sum_hp = 0; 
    bit<48> sum_squares_hp = 0; 
    bit<48> var_hp = 0;
    bit<48> coeff_hp = 0;
    bit<48> abs_number = 0;
    bit<48> squared_num_hp = 0;
  
    // cast signed 32bit value to 48 bits (negative values) 
    abs_number = (bit <48>) abs(number_hp);
    if (number_hp <= ((1 << 31) - 1)) { 
      squared_num_hp = square_48((int<48>) number_hp);
      coeff_hp = abs_number;
    } else {
      squared_num_hp = square_48((int<48>) abs_number);
      coeff_hp = ~abs_number + 1; // Convert to negative 
    }

    lst_sum_hp.read(sum_hp, level);
    sum_hp = sum_hp + coeff_hp;
    lst_sum_hp.write(level, sum_hp);

    sum_of_squares_hp.read(sum_squares_hp, level);
    sum_squares_hp = sum_squares_hp + squared_num_hp; 
    sum_of_squares_hp.write(level, sum_squares_hp);

    squared_sum_hp = square_48((int<48>) sum_hp);
    squared_sum_hp  = division_48(squared_sum_hp, (bit <48>)index + 1);
    var_hp = sum_squares_hp - squared_sum_hp;
    var_hp = division_48(var_hp, (bit <48>) index);
    variance_hp.write(level, var_hp);
    

    if (level == 1) {
      level_one_lp_squares.write(index, squared_num_lp);
      level_one_lp_variance.write(index, var_lp);
      level_one_hp_squares.write(index, squared_num_hp);
      level_one_hp_variance.write(index, var_hp);
    }

    if (level == 2) {
      level_two_lp_squares.write(index, squared_num_lp);
      level_two_lp_variance.write(index, var_lp);
      level_two_hp_squares.write(index, squared_num_hp);
      level_two_hp_variance.write(index, var_hp);
    }

    if (level == 3) {
      level_three_lp_squares.write(index, squared_num_lp);
      level_three_lp_variance.write(index, var_lp);
      level_three_hp_squares.write(index, squared_num_hp);
      level_three_hp_variance.write(index, var_hp);
    }

    if (level == 4) {
      level_four_lp_squares.write(index, squared_num_lp);
      level_four_lp_variance.write(index, var_lp);
      level_four_hp_squares.write(index, squared_num_hp);
      level_four_hp_variance.write(index, var_hp);
    }

    if (level == 5) {
      level_five_lp_squares.write(index, squared_num_lp);
      level_five_lp_variance.write(index, var_lp);
      level_five_hp_squares.write(index, squared_num_hp);
      level_five_hp_variance.write(index, var_hp);
    }

    if (level == 6) {
      level_six_lp_squares.write(index, squared_num_lp);
      level_six_lp_variance.write(index, var_lp);
      level_six_hp_squares.write(index, squared_num_hp);
      level_six_hp_variance.write(index, var_hp);
    }

    if (level == 7) {
      level_seven_lp_squares.write(index, squared_num_lp);
      level_seven_lp_variance.write(index, var_lp);
      level_seven_hp_squares.write(index, squared_num_hp);
      level_seven_hp_variance.write(index, var_hp);
    }

    if (level == 8) {
      level_eight_lp_squares.write(index, squared_num_lp);
      level_eight_lp_variance.write(index, var_lp);
      level_eight_hp_squares.write(index, squared_num_hp);
      level_eight_hp_variance.write(index, var_hp);
    }

    if (level == 9) {
      level_nine_lp_squares.write(index, squared_num_lp);
      level_nine_lp_variance.write(index, var_lp);
      level_nine_hp_squares.write(index, squared_num_hp);
      level_nine_hp_variance.write(index, var_hp);
    }

    if (level == 10) {
      level_ten_lp_squares.write(index, squared_num_lp);
      level_ten_lp_variance.write(index, var_lp);
      level_ten_hp_squares.write(index, squared_num_hp);
      level_ten_hp_variance.write(index, var_hp);
    }
  }
}

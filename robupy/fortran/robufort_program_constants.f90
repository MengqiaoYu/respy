MODULE robufort_program_constants

	!/*	setup	*/

    IMPLICIT NONE

!------------------------------------------------------------------------------- 
!	Parameters and Types
!------------------------------------------------------------------------------- 

    INTEGER, PARAMETER :: our_int   = selected_int_kind(9)
    INTEGER, PARAMETER :: our_sgle  = selected_real_kind(6,37)
    INTEGER, PARAMETER :: our_dble  = selected_real_kind(15,307)

    INTEGER(our_int), PARAMETER :: missing_int  = -99_our_int
    INTEGER(our_int), PARAMETER :: zero_int     = 0_our_int
    INTEGER(our_int), PARAMETER :: one_int      = 1_our_int
    INTEGER(our_int), PARAMETER :: two_int      = 2_our_int
    INTEGER(our_int), PARAMETER :: three_int    = 3_our_int
    INTEGER(our_int), PARAMETER :: four_int     = 4_our_int

    REAL(our_dble), PARAMETER :: missing_dble   = -99_our_dble
    REAL(our_dble), PARAMETER :: zero_dble      = 0.00_our_dble
    REAL(our_dble), PARAMETER :: quarter_dble   = 0.25_our_dble
    REAL(our_dble), PARAMETER :: half_dble      = 0.50_our_dble
    REAL(our_dble), PARAMETER :: one_dble       = 1.00_our_dble
    REAL(our_dble), PARAMETER :: two_dble       = 2.00_our_dble
    REAL(our_dble), PARAMETER :: three_dble     = 3.00_our_dble
    REAL(our_dble), PARAMETER :: four_dble      = 4.00_our_dble

    REAL(our_dble), PARAMETER :: tiny_dble = 1.0e-20_our_dble
    REAL(our_dble), PARAMETER :: pi        = 3.141592653589793238462643383279502884197_our_dble
    
!*******************************************************************************
!*******************************************************************************
END MODULE 
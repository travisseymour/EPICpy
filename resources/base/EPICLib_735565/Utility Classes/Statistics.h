#ifndef STATISTICS_H
#define STATISTICS_H



/*
Use these classes to accumulate running statistics values easily.
reset() - zero the internal variables
update() - add a new data value, updating current average
get_n, mean - return the current values
*/

class Mean_accumulator{
public:
	Mean_accumulator()
		{
			reset();
		}
	void reset()
		{
			n = 0;
			total = 0.0;
			total2 = 0.0;
		}
	
	long get_n() const
		{return n;}
	double get_mean() const
		{return (n > 0) ? (total / n) : 0.0;}
	double get_sample_var() const;
	double get_sample_sd() const;
	double get_est_var() const;
	double get_est_sd() const;
	double get_sdm() const;
	double get_half_95_ci() const;
			
	void update(double x)
		{
			total += x;
			total2 += x*x;
			n++;
		}
			
private:
	long n;
	double total;
	double total2;
};

// accumulates the total number of updates, 
// and the proportion of those updates called with a true argument
class Proportion_accumulator{
public:
	Proportion_accumulator()
		{
			reset();
		}
	void reset()
		{
			count = 0;
			n = 0;
		}
	
	long get_count() const
		{return count;}
	long get_n() const
		{return n;}
	double get_proportion() const
		{return (n > 0) ? double(count) / n : 0.;}
			
	void update(bool count_it)
		{
			n++;
			if(count_it)
				count++;
		}
			
private:
	long count;
	long n;
};

// Accumulate data for a correlation coeficient and regression line
// Like the others, this class uses the one-pass approach which
// can be numerically unreliable under some conditions
class Correl_accumulator {
public:
	Correl_accumulator()
		{reset();}
	void reset()
		{
			n = 0;
			sumx = 0;
			sumy = 0;
			sumxy = 0;
			sumx2 = 0;
			sumy2 = 0;
		}

	void update(double x, double y)
		{
			n++;
			sumx += x;
			sumy += y;
			sumxy += x*y;
			sumx2 += x*x;
			sumy2 += y*y;
		}

	int get_n() const
		{return n;}

	double get_r() const;

	double get_slope() const
		{
			double numerator = n * sumxy - sumx * sumy;
			double denominator = n * sumx2 - sumx * sumx;
			return (denominator > 0.) ? numerator / denominator : 0.0;
		}

	double get_intercept() const
		{
			return (n) ? (sumy - get_slope() * sumx) / n : 0.0;
		}

	double get_rsq() const
		{
			double r = get_r();
			return r*r;
		}

private:
	int n;
	double sumx;
	double sumy;
	double sumxy;
	double sumx2;
	double sumy2;
};

// Give this class object a series of predicted and observed values,
// and then get the goodness-of-fit metrics for them
// using regression fit and simple average absolute error
class PredObs_accumulator {
public:
	PredObs_accumulator() : sumerrorprop(0.)
		{}
	void reset()
		{
			corr.reset();
			sumerrorprop = 0;
		}

	void update(double predicted, double observed)
		{
			corr.update(predicted, observed);
			// compute proportion of absolute error relative to observed value
			sumerrorprop += ((predicted > observed) ? (predicted - observed) : (observed - predicted)) / observed;
		}

	int get_n() const
		{return corr.get_n();}

	double get_rsq() const
		{return corr.get_rsq();}

	double get_slope() const
		{return corr.get_slope();}

	double get_intercept() const
		{return corr.get_intercept();}

	double get_avg_abs_error() const
		{return sumerrorprop / corr.get_n() * 100.;}

private:
	Correl_accumulator corr;
	double sumerrorprop;
};



#endif

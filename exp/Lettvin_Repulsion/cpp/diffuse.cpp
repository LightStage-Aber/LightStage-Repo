//******************************************************************************
// Diffuse.cpp Copyright(c) 2003 Jonathan D. Lettvin, All Rights Reserved.
//******************************************************************************
// Permission to use this code if and only if the first eight lines are first.
// This code is offered under the GPL.
// Please send improvements to the author: jdl@alum.mit.edu
// The User is responsible for errors.
//******************************************************************************
static char *usage_string=
    "QUIT because \"%s\"\n"
    "Usage: %s {Number} [{Jiggle} [{Rounds}]]\n"
    "  Number: count of points to distribute over unit sphere\n"
    "  Jiggle: lower limit of largest movement below which relaxation stops\n"
    "  Rounds: upper limit of relaxation steps above which relaxation stops\n"
    "Fix one charged point at (1,0,0) on a unit sphere.\n"
    "Randomly distribute additional charged points over unit sphere.\n"
    "Prevent identical positioning.\n"
    "Apply formula for charge repulsion to calculate movement vector.\n"
    "After all movement vectors have been calculated, apply to charges.\n"
    "Normalize resulting vectors to constrain movement to sphere.\n"
    "Repeat until movement falls below limit, or rounds rises above limit."
    "Output as a C static double array of coordinate triples."
    ;
//******************************************************************************
// Overview:
// Diffuse a number of points to an approximately stationary position using
// the standard physics formula for charge repulsion (inverse square law)
// over the surface of a sphere.  For vertex counts equalling platonic solids,
// the result will be a distribution approximating that platonic solid.
// Otherwise, distributions are sufficiently random to make
// every possible great circle cross the same number of edges,
// give or take a small variation.
// Use the first point as an anchor at (1,0,0) then randomly distribute points.
// Precautions are taken to avoid identical points (a zerodivide, or "pole").
// The expected area of an inscribed circle around any point should converge to
// the area of the sphere divided by the number of points, therefore the radius
// of said circle should be approximately linear with 1/sqrt(N).  This program
// arbitrarily uses the default minimum incremental movement value .03/sqrt(N).
//******************************************************************************
// OVERALL SEQUENCE OF OPERATION:
// ----
// main: Sequence of operations:
// 1) gather, constrain, and default command-line arguments
// 2) construct "points" object (vector of spherically constrained coordinates)
// 3) output the coordinates calculated during construction
// 4) quit
// ----
// 2: sequence of operations
// a) Initialize random number generator
// b) construct vector of coordinates fixing the first and randomizing others
// c) relax the vector (cause point-charge forces to push points apart)
// d) calculate nearest neighbor for all points and record that minimum radius
// ----
// 2b: sequence of operations
// e) push (1,0,0) on vector
// f) push random normalized coordinates on vector, pop if another is identical
// g) push slot for per-coordinate minimum radius
// ----
// 2c: sequence of operations
// h) for every point get inverse-square increment from all other points
// i) zero the force on the (1,0,0) point to keep anchor
// j) after acquiring all increments, sum and normalize increments, and apply
// k) repeat until maximum movement falls below a minimum
// ----
// 2be and 2bf: sequence of operations
// l) construct either the (1,0,0) point or a random point
// m) normalize to place the point on the unit sphere
// ----
// 2ch: sequence of operations
// n) calculate distance between indexed point and a specific other point
// o) take inverse square of distance
// p) add directly to increment coordinates
// ----
// 2cj: sequence of operations
// q) keep a copy of the starting coordinates for the point
// r) add increment to move point, and normalize it back onto the sphere
// s) calculate distance to starting coordinates and
// t) remember largest movement on surface of sphere
// ----
// 3: sequence of operations
// u) output all point coordinates as a C style static double array
//******************************************************************************
#include <iostream>  // sync_with_stdio
#include <cstdio>    // printf
#include <cstdlib>   // I believe sqrt is in here
#include <ctime>     // Used to salt the random number generator
#include <cmath>     // Various mathematical needs
#include <vector>    // Used to contain many points
#include <valarray>  // Used to implement a true XYZ vector
//******************************************************************************

using namespace std; // Necessary to gain access to many C++ names

//******************************************************************************
typedef valarray<double>coordinates; // To simplify declarations

// A global function to document how to use this program.
void usage(char *program_name,char *quit_reason) {
  fprintf(stderr,usage_string,quit_reason,program_name);
  exit(1);
}
//******************************************************************************
class XYZ { // This class contains operations for placing and moving points
  private:
    double change_magnitude;
    coordinates xyz;   // This holds the coordinates of the point.
    coordinates dxyz;  // This holds the summed force vectors from other points
    inline double random() { return(double((rand()%1000)-500)); } // ordinates
    inline double square(const double& n) { return(n*n); }
    inline coordinates square(const coordinates& n) { return(n*n); }
    inline double inverse(const double& n) { return(1.0/n); }
    XYZ& inverse_square() { xyz*=inverse(square(magnitude())); return *this; }
    inline double magnitude() { return(sqrt((xyz*xyz).sum())); }
    void normalize() { xyz/=magnitude(); } // unit vector
  public:
    XYZ(): xyz(3), dxyz(3) {
      xyz[0]=random(); xyz[1]=random(); xyz[2]=random(); normalize();
    }
    XYZ(const double& x,const double& y,const double& z) : xyz(3), dxyz(3) {
      xyz[0]=x; xyz[1]=y; xyz[2]=z;
    }
    XYZ(const coordinates& p) : xyz(3), dxyz(3) {
      xyz=p;
    }
    ~XYZ() { }
    coordinates& array() { return xyz; }
    void zero_force() { dxyz=0.0; }
    double change() { return(change_magnitude); }
    double magnitude(XYZ& b) { // Return length of vector.  (not const)
      return(sqrt( square(b.array()-xyz).sum() ));
    }
    void sum_force(XYZ& b) { // Cause force from each point to sum.  (not const)
      dxyz+=(XYZ(b.array()-xyz).inverse_square().array()); // Calculate and add
    }
    void move_over_sphere() { // Cause point to move due to force
      coordinates before=xyz;                       // Save previous position
      xyz-=dxyz;                                    // Follow movement vector
      normalize();                                  // Project back to sphere
      before-=xyz;                                  // Calculate traversal
      change_magnitude=sqrt((before*before).sum()); // Record largest
    }
    void report(const double& d) {
      printf("  { %+1.3e,%+1.3e,%+1.3e,%+1.3e }",xyz[0],xyz[1],xyz[2],d);
    }
};

//******************************************************************************
class points { // This class organizes expression of relations between points
  private:
    const size_t N;   // Number of point charges on surface of sphere
    const size_t R;   // Number of rounds after which to stop
    const double L;   // Threshold of movement below which to stop
    char        *S;   // Name of this vertex set
    size_t rounds;    // Index of rounds processed
    vector<XYZ>V;     // List of point charges
    vector<double>H;  // List of minimum distances
    double maximum_change; // The distance traversed by the most moved point
    double minimum_radius; // The radius of the smallest circle
    time_t T0;        // Timing values

    void relax() { // Cause all points to sum forces from all other points
      size_t i, j;
      rounds=0;
      do {
        maximum_change=0.0;
        for(i=1;i<N;i++) {   // for all points other than the fixed point
          V[i].zero_force();                       // Initialize force vector
          for(j=  0;j<i;j++) V[i].sum_force(V[j]); // Get contributing forces
          // Skip i==j
          for(j=i+1;j<N;j++) V[i].sum_force(V[j]); // Get contributing forces
        }
        for(i=1;i<N;i++) {  // React to summed forces except for the fixed point
          V[i].move_over_sphere();
          if(V[i].change()>maximum_change) maximum_change=V[i].change();
        }
        ++rounds;
      } while(maximum_change>L); //&&++rounds<R); // Until small or too much movement
    }
  public:
    points(char *s,const size_t& n,const double& l,const size_t& r) :
      N(n), L(l), R(r)
    {
      S=s;
      T0=time(0L);                   // Get the current time
      srand(T0);                     // Salt the random number generator.
      V.push_back(XYZ(1.0,0.0,0.0)); // Create Anchored first point V[0] (1,0,0)
      H.push_back(2.0);
      while(V.size()<N) {   // For all other points, until we have enough
	    V.push_back(XYZ()); // Create randomized position
        H.push_back(2.0);
        coordinates& last=V.back().array(); // Remember this position
        for(size_t i=V.size()-1;i--;) { // And check to see if it is occupied
          coordinates& temp=V[i].array();
          if(temp[0]==last[0]&&temp[1]==last[1]&&temp[2]==last[2]) {
            V.pop_back(); // Remove the position if it is already occupied
            break;
          }
        }
      }
      relax();  // After vector construction, start the relaxation process
      size_t i, j;
      minimum_radius=1.0; // On a unit sphere, the maximum circle radius is 1.0
      for(i=0;i<V.size();i++) { // Discover the minimum distance between points.
        for(j=0;j<V.size();j++) {
          if(j==i) continue;
          double rtemp=V[i].magnitude(V[j])/2.0;
          if(rtemp<minimum_radius) minimum_radius=rtemp; // Record when smaller.
          if(rtemp<H[i]) H[i]=rtemp;
        }
      }
    }
    ~points() {}
    coordinates& operator[](const size_t& i) { // Caller access to positions
      return(V[i].array());
    }
    void report() { // Output run statistics and positions of all points
      printf(
	  "/* Rounds   =%d/%d */\n"
	  "/* Jiggle dV=%+1.2e/%+1.2e */\n"
	  "/* minimum r=%+1.2e */\n"
	  "/* elapsed time<=%ld seconds. */\n"
	  "static size_t points_%s=%d;\n"
	  "static double vertex_%s[%d][4] = {\n"
	  "/*{  X         , Y         , Z         , Rmin       } */\n"
	  ,
	  rounds,R,maximum_change,L,minimum_radius,1L+time(0L)-T0,S,N,S,N);
      V[0].report(H[0]);
      for(size_t i=1;i<N;i++) { printf(",\n"); V[i].report(H[i]); }
      printf("\n};\n");
    }
};

//******************************************************************************
int main(int argc,char **argv) {
  ios::sync_with_stdio(true); // Not needed because iostream is not used.
  size_t Number=0;            // Cause point count to have a failing value.
  size_t Rounds=0;        // Stop relaxation after this number of rounds.
  double Jiggle;              // Stop relaxation when movement drops below.

  if(argc<2||argc>4)
    usage(argv[0],"Bad argument count");
  if((Number=atoi(argv[1]))<2)
    usage(argv[0],"Constrain Number>1");
  Jiggle=0.03/sqrt(double(Number));     // default Jiggle=.03 of expected radius
  if(argc>=3&&((Jiggle=atof(argv[2]))<=0||Jiggle>(0.03/sqrt(double(Number)))))
    usage(argv[0],"Constrain 0<Jiggle<0.03/sqrt(Number)");
  //if(argc==4&&(Rounds=atoi(argv[3]))<50||Rounds>10000)
  //  usage(argv[0],"Constrain 50<=Rounds<=10000");
  points P("default",Number,Jiggle,Rounds);
  // P can now be addressed for specific XYZ values for scaling and reporting
  // For instance P[0] should return a valarray& of three elements (1,0,0)
  // In this program, the array is simply output as a C static double array
  P.report();
  return(0);
}
//******************************************************************************
// End of file
//******************************************************************************

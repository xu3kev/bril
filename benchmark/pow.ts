let pow = 40;
let x = 3;
let result = 1;
for (let i = pow; i > 0; ) {
  if(i/2*2 == i){
  }
  else{
    result = result * x;
  }
  x = x * x;
  i = i/2;
}
console.log(result);

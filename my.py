#배열내에서 값 꺼내오기 연습
import matplotlib.pyplot as plt
import numpy as np
#
# x=[1,2,3]
# y=[1,2,3]
#
# plt.plot(x,y)
# plt.show()


Y = np.random.random(10)

plt.hist(Y, bins=10)
plt.show()
import matplotlib.pyplot as plt
import pandas as pd

fig, ax= plt.subplots()
ax.set_xticks([])
ax.set_yticks([])
plt.title('Mapa de Produtividade')
plt.savefig('/tmp/newtest1.png')

plt.close(fig)

# Introduction:

## Abstract:
> Cross modal retrieval receives intensive attention for flexible queries between different modalities. However, in practice it is challenging to retrieve cross modal content with noisy labels. The latest research on machine learning shows that a model tends to fit cleanly labeled data at early learning stage and then memorize the data with noisy labels. Although the clustering strategy in cross modal retrieval can be utilized for alleviating outliers, the networks will rapidly overfit after clean data is fitted well and the noisy labels begin to force the cluster center drift. Motivated by these fundamental phenomena, we propose an Early Learning regularized Contrastive Learning method for Cross Modal Retrieval with Noisy Labels (ELRCMR). In the solution, we propose to project the multi-modal data to a shared feature space by contrastive learning, in which early learning regularization is employed to prevent the memorization of noisy labels when training the model, and the dynamic weight balance strategy is employed to alleviate clustering drift. We evaluated the method with extensive experiments, and the result shows the proposed method could solve the cluster drift in conventional solutions and achieve promising performance on widely used benchmark datasets.

## conda env:
```
name: papers
channels:
  - pytorch
  - defaults
dependencies:
  - _libgcc_mutex=0.1=main
  - blas=1.0=mkl
  - ca-certificates=2020.6.24=0
  - certifi=2020.6.20=py37_0
  - cffi=1.14.0=py37he30daa8_1
  - cuda100=1.0=0
  - intel-openmp=2020.1=217
  - ld_impl_linux-64=2.33.1=h53a641e_7
  - libedit=3.1.20191231=h14c3975_1
  - libffi=3.3=he6710b0_2
  - libgcc-ng=9.1.0=hdf63c60_0
  - libgfortran-ng=7.3.0=hdf63c60_0
  - libstdcxx-ng=9.1.0=hdf63c60_0
  - mkl=2020.1=217
  - mkl-service=2.3.0=py37he904b0f_0
  - mkl_fft=1.1.0=py37h23d657b_0
  - mkl_random=1.1.1=py37h0573a6f_0
  - ncurses=6.2=he6710b0_1
  - ninja=1.9.0=py37hfd86e86_0
  - numpy=1.18.5=py37ha1c710e_0
  - numpy-base=1.18.5=py37hde5b4d6_0
  - openssl=1.1.1g=h7b6447c_0
  - pip=20.1.1=py37_1
  - pycparser=2.20=py_2
  - python=3.7.7=hcff3b4d_5
  - pytorch=0.4.1=py37_py36_py35_py27__9.0.176_7.1.2_2
  - readline=8.0=h7b6447c_0
  - setuptools=49.2.0=py37_0
  - six=1.15.0=py_0
  - sqlite=3.32.3=h62c20be_0
  - tk=8.6.10=hbc83047_0
  - wheel=0.34.2=py37_0
  - xz=5.2.5=h7b6447c_0
  - zlib=1.2.11=h7b6447c_3
  - pip:
    - boto==2.49.0
    - boto3==1.14.28
    - botocore==1.17.28
    - chardet==3.0.4
    - cssselect==1.1.0
    - cycler==0.10.0
    - decorator==4.4.2
    - docutils==0.15.2
    - gensim==3.8.3
    - idna==2.10
    - imageio==2.9.0
    - jmespath==0.10.0
    - kiwisolver==1.2.0
    - lxml==4.5.2
    - matplotlib==3.3.0
    - networkx==2.4
    - objgraph==3.4.1
    - pillow==7.2.0
    - pyparsing==2.4.7
    - pyquery==1.4.1
    - python-dateutil==2.8.1
    - python-graphviz==0.14.1
    - pywavelets==1.1.1
    - requests==2.24.0
    - s3transfer==0.3.3
    - scikit-image==0.17.2
    - scipy==1.5.2
    - smart-open==2.1.0
    - tifffile==2020.7.24
    - torchvision==0.2.1
    - urllib3==1.25.10
prefix: /home/anaconda3/envs/papers
```

# Dataset url:

***INRIA-websearch***
[图片1](ftp://ftp.inrialpes.fr/pub/lear/douze/data/jpg1.tar.gz), [图片2](ftp://ftp.inrialpes.fr/pub/lear/douze/data/jpg2.tar.gz), [文本描述](ftp://ftp.inrialpes.fr/pub/lear/douze/data/siftgeo.tar.gz)

***xmedianet***
[link](http://59.108.48.34/tiki/XMediaNet/)
***Wikipedia***
[link](http://www.svcl.ucsd.edu/projects/crossmodal/)

# Running:

> xmedianet dataset:
> python -u main_noisy.py --max_epochs 100 --log_name noisylabel_mce --loss MCE --lr 0.0001 --train_batch_size 500 --lama 0.001 --zeta 0.001 --beta 1 --alpha 1 --setp 100000 --betasetp 50000 --noisy_ratio 0.4 --data_name xmedianet
> 
> INRIA dataset
> python -u main_noisy.py --max_epochs 100 --log_name noisylabel_mce --loss MCE --lr 0.0001 --train_batch_size 100 --lama 0.001 --zeta 0.001 --beta 1 --alpha 1 --setp 100000 --betasetp 10000 --noisy_ratio 0.8 --data_name inria
>
> Wikipedia dataset
>python -u main_noisy.py --max_epochs 100 --log_name noisylabel_mce --loss MCE --lr 0.0001 --train_batch_size 100 --lama 1 --zeta 0.001 --beta 0.75  --noisy_ratio 0.6 --alpha 1 --setp 100000 --betasetp 3000 --data_name wiki  
完整代码见：https://pan.baidu.com/s/1zksJOwmF2tkTiy3UOE6jfA?pwd=t6eq
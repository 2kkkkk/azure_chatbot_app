删除本地和azure的registry docker镜像，删除azure app 服务。

`docker login llmappexpregistry.azurecr.io --username yourusername --password yourpassword`(可能 要开代理)

（如果直接docker build报错）`docker pull original_image_name`(挂梯子，有的梯子可能也不好用，，已经pull了可以跳过)



(**build 之前检查 dockfile**)`docker build -t llmappexpregistry.azurecr.io/botapp:v1 .`（挂梯子，有的梯子可能也不好用）

 `docker push llmappexpregistry.azurecr.io/botapp:v1 `（不用梯子）

新建azure app service 



------

如果使用langchain,那么不同的llm可能不兼容，比如chatopenai模型可以使用create_dataframe_agent跑通chat_pandas_df代码，换成gemini模型就会报错，兼容性比较差。

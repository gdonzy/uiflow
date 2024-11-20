# 定义变量
FRONTEND_DIR := web
BACKEND_DIR := server
STATIC_DIR := static
FRONTEND_BUILD_DIR := $(FRONTEND_DIR)/dist

# 默认目标
.PHONY: build
build: frontend backend

# 构建前端
.PHONY: frontend
frontend:
	@echo "=== Building frontend ==="
	cd $(FRONTEND_DIR) && npm install && npm run build:pro
	@echo "=== Copying frontend build files to static directory ==="
	mkdir -p $(STATIC_DIR)
	cp -r $(FRONTEND_BUILD_DIR)/* $(STATIC_DIR)

# 构建后端
.PHONY: backend
backend:
	@echo "=== Building backend with pyinstaller ==="
	python -m pip install -r requirements.txt
	python build.py
	@echo "=== Backend build complete ==="

# 清理前端和后端构建的文件
.PHONY: clean
clean:
	@echo "=== Cleaning up frontend and backend build files ==="
	rm -rf $(STATIC_DIR)
	rm -rf $(FRONTEND_DIR)/node_modules
	rm -rf $(FRONTEND_DIR)/dist
	rm -rf $(BACKEND_DIR)/dist
	rm -rf $(BACKEND_DIR)/build
	rm -f $(BACKEND_DIR)/*.spec
	rm -rf dist
	rm -rf build
	rm -rf *.spec

